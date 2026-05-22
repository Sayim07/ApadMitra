import logging
from dataclasses import dataclass
from typing import Dict, Any, List
import time
import asyncio

from services.notification_service import SMSService, WhatsAppService, EmailService, DashboardService
from services.voice_service import VoiceCallService
from services.firebase_service import firebase_service
from config.settings import settings
from utils.retry_queue import AsyncRetry
try:
    from api.routes.metrics import ALERTS_DISPATCHED
except Exception:
    ALERTS_DISPATCHED = None

logger = logging.getLogger("dispatch_agent")


@dataclass
class DispatchResult:
    channels_attempted: List[str]
    channels_succeeded: List[str]
    channels_failed: List[str]
    dispatch_timestamp: float
    alert_ids: List[str]


class DispatchAgent:
    def __init__(self):
        self.role = "Emergency Alert Dispatch Coordinator"
        self.sms = SMSService(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER)
        self.wa = WhatsAppService(settings.GUPSHUP_API_KEY, settings.GUPSHUP_APP_NAME)
        self.email = EmailService(settings.SENDGRID_API_KEY)
        self.dashboard = DashboardService()
        self.voice = VoiceCallService(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER)
        self.retry = AsyncRetry(retries=3, base_delay=0.5, max_delay=8.0)

    async def _send_sms(self, to: str, body: str):
        try:
            return await self.retry.run(self.sms.send_sms, to, body)
        except Exception:
            logger.exception("sms send error")
            return None

    async def _send_whatsapp(self, to: str, body: str):
        try:
            return await self.retry.run(self.wa.send_whatsapp, to, body)
        except Exception:
            logger.exception("whatsapp send error")
            return None

    async def _send_email(self, to: str, subject: str, html: str):
        try:
            return await self.retry.run(self.email.send_email, to, subject, html)
        except Exception:
            logger.exception("email send error")
            return None

    async def _send_voice(self, to: str, script: str, incident_id: str):
        try:
            return await self.retry.run(self.voice.place_emergency_call, to, script, incident_id)
        except Exception:
            logger.exception("voice call error")
            return None

    async def dispatch_all(self, incident_id: str) -> DispatchResult:
        incident = await firebase_service.get_incident(incident_id)
        if not incident:
            return DispatchResult([], [], [], time.time(), [])

        severity = incident.get("severity", "GREEN")
        channels_attempted = []
        channels_succeeded = []
        channels_failed = []
        alert_ids = []

        # prepare messages
        msg = f"{incident.get('disaster_type')} at {incident.get('location_name')}. Severity: {severity}. Follow instructions."

        # get authority contacts to notify
        contacts = await firebase_service.get_authority_contacts(incident.get('district'))
        phone_numbers = [c.get('phone') for c in contacts if c.get('phone')]
        emails = [c.get('email') for c in contacts if c.get('email')]

        tasks = []

        if severity == "RED":
            # all channels
            channels_attempted += ["SMS", "WHATSAPP", "EMAIL", "VOICE", "DASHBOARD"]
            for p in phone_numbers:
                tasks.append(self._send_sms(p, msg))
                tasks.append(self._send_whatsapp(p, msg))
                tasks.append(self._send_voice(p, f"Emergency: {msg}", incident_id))
            for e in emails:
                tasks.append(self._send_email(e, f"Emergency: {incident.get('location_name')}", msg))
            tasks.append(self.dashboard.push_update(incident_id, {"status": "DISPATCHED"}))

        elif severity == "YELLOW":
            channels_attempted += ["SMS", "WHATSAPP", "EMAIL", "DASHBOARD"]
            for p in phone_numbers:
                tasks.append(self._send_sms(p, msg))
                tasks.append(self._send_whatsapp(p, msg))
            for e in emails:
                tasks.append(self._send_email(e, f"Alert: {incident.get('location_name')}", msg))
            tasks.append(self.dashboard.push_update(incident_id, {"status": "DISPATCHED"}))

        else:
            channels_attempted += ["DASHBOARD"]
            tasks.append(self.dashboard.push_update(incident_id, {"status": "PUSHED"}))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, Exception) or res is None:
                channels_failed.append(str(res))
            else:
                channels_succeeded.append(str(res))
                # if Twilio/SMS returned sid, create/update alert
                try:
                    if isinstance(res, dict) and res.get('sid') is not None:
                        alert_ids.append(res.get('sid'))
                except Exception:
                    pass

        # update incident record
        await firebase_service.update_incident(incident_id, {"channels_dispatched": channels_succeeded, "alerts_sent": alert_ids, "updated_at": time.time()})

        # increment metrics if available
        try:
            if ALERTS_DISPATCHED is not None and alert_ids:
                ALERTS_DISPATCHED.inc(len(alert_ids))
        except Exception:
            logger.exception("Failed to increment ALERTS_DISPATCHED metric")

        return DispatchResult(channels_attempted=channels_attempted, channels_succeeded=channels_succeeded, channels_failed=channels_failed, dispatch_timestamp=time.time(), alert_ids=alert_ids)
