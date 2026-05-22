import logging
import asyncio
from typing import List, Dict, Optional

logger = logging.getLogger("notification_service")

try:
    from twilio.rest import Client as TwilioClient
except Exception:
    TwilioClient = None

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except Exception:
    SendGridAPIClient = None

import httpx


class SMSService:
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None, from_number: Optional[str] = None):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self._client = TwilioClient(account_sid, auth_token) if TwilioClient and account_sid and auth_token else None

    async def send_sms(self, to: str, body: str) -> Dict:
        if self._client:
            try:
                loop = asyncio.get_event_loop()
                msg = await loop.run_in_executor(None, lambda: self._client.messages.create(body=body, from_=self.from_number, to=to))
                logger.info("twilio sms sent to=%s sid=%s", to, getattr(msg, 'sid', None))
                return {"sid": getattr(msg, 'sid', None), "status": getattr(msg, 'status', 'sent'), "to": to}
            except Exception:
                logger.exception("twilio send failed")
                return {"sid": None, "status": "failed", "to": to}

        logger.info("send_sms placeholder to=%s", to)
        return {"sid": None, "status": "queued", "to": to}

    async def send_bulk_sms(self, contacts: List[str], body: str) -> List[Dict]:
        tasks = [self.send_sms(c, body) for c in contacts]
        return await asyncio.gather(*tasks)


class WhatsAppService:
    def __init__(self, api_key: Optional[str] = None, app_name: Optional[str] = None, twilio_from: Optional[str] = None, twilio_client: TwilioClient = None):
        self.api_key = api_key
        self.app_name = app_name
        self.twilio_from = twilio_from
        self._twilio = twilio_client

    async def send_whatsapp(self, to: str, body: str) -> Dict:
        # Prefer Twilio WhatsApp if available
        if self._twilio and self.twilio_from:
            try:
                loop = asyncio.get_event_loop()
                msg = await loop.run_in_executor(None, lambda: self._twilio.messages.create(body=body, from_=f"whatsapp:{self.twilio_from}", to=f"whatsapp:{to}"))
                logger.info("twilio whatsapp sent to=%s sid=%s", to, getattr(msg, 'sid', None))
                return {"sid": getattr(msg, 'sid', None), "status": getattr(msg, 'status', 'sent'), "to": to}
            except Exception:
                logger.exception("twilio whatsapp failed")

        # Fallback to Gupshup HTTP API if key provided
        if self.api_key and self.app_name:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    payload = {"app": self.app_name, "to": to, "message": body}
                    headers = {"api_key": self.api_key}
                    r = await client.post("https://api.gupshup.io/sm/api/v1/msg", json=payload, headers=headers)
                    if r.status_code in (200, 201):
                        return {"status": "sent", "to": to}
            except Exception:
                logger.exception("gupshup send failed")

        logger.info("send_whatsapp placeholder to=%s", to)
        return {"status": "queued", "to": to}


class EmailService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._client = SendGridAPIClient(api_key) if SendGridAPIClient and api_key else None

    async def send_email(self, to: str, subject: str, html_content: str) -> Dict:
        if self._client:
            try:
                message = Mail(from_email=("noreply@aapdamitra.local", "AapdaMitra"), to_emails=to, subject=subject, html_content=html_content)
                loop = asyncio.get_event_loop()
                resp = await loop.run_in_executor(None, lambda: self._client.send(message))
                logger.info("sendgrid email status=%s to=%s", getattr(resp, 'status_code', None), to)
                return {"status": getattr(resp, 'status_code', None), "to": to}
            except Exception:
                logger.exception("sendgrid send failed")
                return {"status": "failed", "to": to}

        logger.info("send_email placeholder to=%s subject=%s", to, subject)
        return {"status": "queued", "to": to}

    async def send_district_report(self, to: str, incident: Dict, html_report: str) -> Dict:
        return await self.send_email(to, f"District Report: {incident.get('location_name')}", html_report)


class DashboardService:
    def __init__(self):
        pass

    async def push_update(self, incident_id: str, update_data: Dict) -> None:
        # write to Firestore /live_updates/{incident_id} could be implemented here
        logger.info("push_update placeholder for %s data=%s", incident_id, update_data)
