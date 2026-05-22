import logging
import asyncio
from typing import List, Dict, Optional

logger = logging.getLogger("voice_service")

try:
    from twilio.rest import Client as TwilioClient
except Exception:
    TwilioClient = None


class VoiceCallService:
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None, from_number: Optional[str] = None):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self._client = TwilioClient(account_sid, auth_token) if TwilioClient and account_sid and auth_token else None

    async def place_emergency_call(self, to: str, script: str, incident_id: str) -> Dict:
        twiml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Say voice=\"alice\" language=\"en-IN\">{script}</Say><Hangup/></Response>"
        if self._client:
            try:
                loop = asyncio.get_event_loop()
                # use twiml param to avoid hosting a public URL for now
                call = await loop.run_in_executor(None, lambda: self._client.calls.create(twiml=twiml, to=to, from_=self.from_number))
                logger.info("twilio call placed to=%s sid=%s", to, getattr(call, 'sid', None))
                return {"call_sid": getattr(call, 'sid', None), "status": getattr(call, 'status', 'queued'), "to": to, "incident_id": incident_id}
            except Exception:
                logger.exception("twilio call failed")
                return {"call_sid": None, "status": "failed", "to": to, "incident_id": incident_id}

        logger.info("place_emergency_call placeholder to=%s incident=%s", to, incident_id)
        return {"call_sid": None, "status": "queued", "to": to, "incident_id": incident_id}

    async def place_bulk_calls(self, contacts: List[str], script: str, incident_id: str) -> List[Dict]:
        sem = asyncio.Semaphore(8)

        async def _call(to):
            async with sem:
                return await self.place_emergency_call(to, script, incident_id)

        tasks = [_call(c) for c in contacts]
        return await asyncio.gather(*tasks)

    def build_twiml_for_incident(self, incident: Dict, language: str = "en") -> str:
        script = incident.get("voice_script") or f"Emergency: {incident.get('disaster_type')} at {incident.get('location_name')}"
        twiml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Say voice=\"alice\" language=\"en-IN\">{script}</Say></Response>"
        return twiml
