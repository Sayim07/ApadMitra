import logging
from dataclasses import dataclass
from typing import Dict, Any, List
import time

from services.firebase_service import firebase_service
from config.settings import settings

logger = logging.getLogger("alert_generation_agent")


@dataclass
class GeneratedAlert:
    incident_id: str
    alert_type: str
    language: str
    channel: str
    content_text: str
    content_html: str
    generated_at: float


class AlertGenerationAgent:
    def __init__(self):
        self.role = "Emergency Communications Specialist"
        # try import genai if available
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.genai = genai
        except Exception:
            self.genai = None

    async def generate_citizen_alert(self, incident: Dict[str, Any], language: str = "en") -> str:
        # Short urgent alert for citizens
        text = f"{incident.get('disaster_type')} at {incident.get('location_name')}. {incident.get('raw_text')}. Take shelter and follow local authority instructions."
        if self.genai:
            try:
                prompt = f"Generate a SHORT urgent citizen alert in {language} (max 160 chars for SMS).\n\nIncident: {incident.get('disaster_type')} in {incident.get('location_name')}\nSeverity: {incident.get('severity')}\nDetails: {incident.get('raw_text')}"
                resp = self.genai.generate_text(model="gemini-1.5-flash", prompt=prompt, max_output_tokens=120)
                out = resp.text if hasattr(resp, 'text') else str(resp)
                return out[:300]
            except Exception:
                logger.exception("gemini generate_citizen_alert failed")
        return text[:300]

    async def generate_authority_brief(self, incident: Dict[str, Any]) -> str:
        text = f"Incident: {incident.get('disaster_type')} at {incident.get('location_name')}. Verification score: {incident.get('verification_score')}. Priority: {incident.get('priority_score')}."
        if self.genai:
            try:
                prompt = f"Generate a formal emergency incident brief (English) for authorities. Incident JSON: {incident}" 
                resp = self.genai.generate_text(model="gemini-1.5-flash", prompt=prompt, max_output_tokens=500)
                return resp.text[:400]
            except Exception:
                logger.exception("gemini authority brief failed")
        return text

    async def generate_voice_call_script(self, incident: Dict[str, Any], language: str = "en") -> str:
        script = f"Hello, this is an emergency alert from AapdaMitra. {incident.get('disaster_type')} reported at {incident.get('location_name')}. Severity {incident.get('severity')}. Say ACKNOWLEDGED to confirm receipt."
        return script[:400]

    async def generate_all_alerts(self, incident_id: str) -> List[GeneratedAlert]:
        incident = await firebase_service.get_incident(incident_id)
        if not incident:
            return []

        languages = ["en", "hi", "bn"]
        generated = []
        for lang in languages:
            citizen_text = await self.generate_citizen_alert(incident, lang)
            ga = GeneratedAlert(incident_id=incident_id, alert_type="CITIZEN", language=lang, channel="SMS", content_text=citizen_text, content_html="", generated_at=time.time())
            alert_id = await firebase_service.create_alert(ga.__dict__)
            generated.append(ga)

        # authority brief (English)
        brief = await self.generate_authority_brief(incident)
        ga2 = GeneratedAlert(incident_id=incident_id, alert_type="AUTHORITY_BRIEF", language="en", channel="EMAIL", content_text=brief, content_html=brief, generated_at=time.time())
        await firebase_service.create_alert(ga2.__dict__)
        generated.append(ga2)

        # voice script
        vs = await self.generate_voice_call_script(incident, "en")
        ga3 = GeneratedAlert(incident_id=incident_id, alert_type="VOICE_SCRIPT", language="en", channel="VOICE", content_text=vs, content_html="", generated_at=time.time())
        await firebase_service.create_alert(ga3.__dict__)
        generated.append(ga3)

        return generated
