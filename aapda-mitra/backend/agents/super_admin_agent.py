import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import settings
from services.firebase_service import firebase_service
from models.user import UserRole

logger = logging.getLogger("super_admin_agent")

try:
    from agents.pipeline import pipeline
except Exception:
    pipeline = None


DEFAULT_AUTHORITY_TYPES = [
    "FLOOD",
    "FIRE",
    "EARTHQUAKE",
    "CYCLONE",
    "LANDSLIDE",
    "ROAD_DAMAGE",
    "TREE_FALL",
    "ELECTRICITY",
    "MEDICAL",
    "GENERAL",
]


def _heuristic_route(text: str) -> List[str]:
    t = (text or "").lower()
    out: List[str] = []
    rules = [
        ("road", "ROAD_DAMAGE"),
        ("bridge", "ROAD_DAMAGE"),
        ("pothole", "ROAD_DAMAGE"),
        ("tree", "TREE_FALL"),
        ("fallen tree", "TREE_FALL"),
        ("wire", "ELECTRICITY"),
        ("electric", "ELECTRICITY"),
        ("pole", "ELECTRICITY"),
        ("fire", "FIRE"),
        ("smoke", "FIRE"),
        ("flood", "FLOOD"),
        ("water", "FLOOD"),
        ("earthquake", "EARTHQUAKE"),
        ("tremor", "EARTHQUAKE"),
        ("cyclone", "CYCLONE"),
        ("storm", "CYCLONE"),
        ("landslide", "LANDSLIDE"),
        ("collapse", "LANDSLIDE"),
        ("injury", "MEDICAL"),
        ("ambulance", "MEDICAL"),
        ("medical", "MEDICAL"),
    ]
    for k, v in rules:
        if k in t:
            out.append(v)
    if not out:
        out.append("GENERAL")
    return sorted(list(set(out)))


class SuperAdminAgent:
    def __init__(self):
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.genai = genai
        except Exception:
            self.genai = None

    async def _route_followup(self, incident: Dict) -> List[str]:
        text = (incident.get("raw_text") or "").strip()
        hinted = incident.get("target_authority_types") or []
        if hinted:
            return [str(x).upper() for x in hinted if x]

        if self.genai and settings.GEMINI_API_KEY:
            try:
                prompt = (
                    "You are an emergency operations AI. "
                    "Classify this report into one or more authority types from this list:\n"
                    f"{DEFAULT_AUTHORITY_TYPES}\n\n"
                    "Return ONLY a JSON array of strings.\n\n"
                    f"Report text:\n{text}"
                )
                resp = self.genai.generate_text(model="gemini-1.5-flash", prompt=prompt, max_output_tokens=120)
                raw = resp.text if hasattr(resp, "text") else str(resp)
                raw = raw.strip()
                if raw.startswith("```"):
                    raw = raw.strip("`")
                import json
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    cleaned = [str(x).upper() for x in parsed if x]
                    cleaned = [x for x in cleaned if x in DEFAULT_AUTHORITY_TYPES]
                    if cleaned:
                        return sorted(list(set(cleaned)))
            except Exception:
                logger.exception("Gemini routing failed; falling back to heuristic")

        return _heuristic_route(text)

    async def process_followups_once(self) -> int:
        pending = await firebase_service.get_pending_followup_incidents(limit=50)
        handled = 0
        for inc in pending:
            followup_id = inc.get("document_id")
            if not followup_id:
                continue
            targets = await self._route_followup(inc)
            try:
                await firebase_service.update_incident(
                    followup_id,
                    {
                        "target_authority_types": targets,
                        "routing_status": "ROUTED",
                        "updated_at": datetime.utcnow(),
                    },
                )
                try:
                    await firebase_service.create_incident_action(
                        followup_id,
                        {"action": "super_admin_route", "by": "AI_SUPER_ADMIN", "details": {"target_authority_types": targets}, "ts": datetime.utcnow()},
                    )
                except Exception:
                    pass
                try:
                    if pipeline is not None:
                        await pipeline.enqueue_incident(followup_id)
                except Exception:
                    pass
                handled += 1
            except Exception:
                logger.exception("Failed to update follow-up %s", followup_id)
                try:
                    await firebase_service.update_incident(followup_id, {"routing_status": "FAILED", "updated_at": datetime.utcnow()})
                except Exception:
                    pass
        return handled

    async def process_authority_requests_once(self) -> int:
        reqs = await firebase_service.get_pending_authority_requests(limit=50)
        handled = 0
        for r in reqs:
            request_id = r.get("request_id")
            uid = r.get("user_id")
            if not request_id or not uid:
                continue
            requested_role = r.get("requested_role") or UserRole.DISTRICT_AUTHORITY.value
            authority_types = r.get("authority_types") or []
            district = r.get("district")
            name = r.get("name")
            phone = r.get("phone")

            updates = {
                "user_id": uid,
                "name": name,
                "phone": phone,
                "role": requested_role,
                "preferences": {
                    "district": district,
                    "authority_types": authority_types,
                },
            }
            try:
                await firebase_service.create_user_profile(uid, updates)
                await firebase_service.update_authority_request(request_id, {"status": "APPROVED", "approved_at": datetime.utcnow(), "updated_at": datetime.utcnow()})
                handled += 1
            except Exception:
                logger.exception("Failed to approve authority request %s", request_id)
                try:
                    await firebase_service.update_authority_request(request_id, {"status": "FAILED", "updated_at": datetime.utcnow()})
                except Exception:
                    pass
        return handled

    async def run(self) -> None:
        while True:
            try:
                await self.process_authority_requests_once()
            except Exception:
                logger.exception("Authority request processing loop error")
            try:
                await self.process_followups_once()
            except Exception:
                logger.exception("Follow-up routing loop error")
            await asyncio.sleep(5)


super_admin_agent = SuperAdminAgent()
