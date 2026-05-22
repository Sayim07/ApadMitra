from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from services.firebase_service import firebase_service
from api.middleware.auth import require_role
from models.user import UserRole
from fastapi import Request

import logging
import asyncio
from services.notification_queue import notification_queue

logger = logging.getLogger("alerts_router")

router = APIRouter(prefix="/alerts")


@router.get("")
async def list_alerts(skip: int = 0, limit: int = 50, incident_id: Optional[str] = None):
    filters = {}
    if incident_id:
        filters["incident_id"] = incident_id
    # simple implementation: list alerts via Firestore query
    alerts = await firebase_service.get_alerts_for_incident(incident_id) if incident_id else []
    return {"results": alerts}


@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    # fetch single alert document
    alert = await firebase_service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.put("/{alert_id}/status")
async def update_alert_status(alert_id: str, body: dict):
    status_str = body.get("status")
    delivered_at = body.get("delivered_at")
    await firebase_service.update_alert_status(alert_id, status_str, delivered_at)
    return {"ok": True}


@router.post("/broadcast", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def broadcast_alert(body: dict):
    # body: {district, message, channels?: ["sms","email"]}
    district = body.get("district")
    message = body.get("message")
    channels = body.get("channels", ["sms", "email"])
    if not district or not message:
        raise HTTPException(status_code=400, detail="district and message required")

    # create alert record
    alert_data = {"district": district, "provider": "ADMIN_BROADCAST", "message": message, "delivery_status": "PENDING", "created_at": datetime.utcnow()}
    try:
        alert_id = await firebase_service.create_alert(alert_data)
    except Exception:
        alert_id = None

    # get authority contacts
    contacts = await firebase_service.get_authority_contacts(district)

    # enqueue notifications
    for c in contacts:
        try:
            if "sms" in channels and c.get("phone"):
                item = {"alert_id": alert_id, "channel": "sms", "to": c.get("phone"), "message": message}
                try:
                    asyncio.create_task(notification_queue.enqueue(item))
                except Exception:
                    await notification_queue.enqueue(item)
            if "email" in channels and c.get("email"):
                item = {"alert_id": alert_id, "channel": "email", "to": c.get("email"), "subject": f"Broadcast: {district}", "html": message}
                try:
                    asyncio.create_task(notification_queue.enqueue(item))
                except Exception:
                    await notification_queue.enqueue(item)
        except Exception:
            logging.exception("Failed to enqueue broadcast notification for contact")

    return {"ok": True, "alert_id": alert_id}



@router.post('/webhook/twilio/message-status')
async def twilio_message_status(request: Request):
    form = await request.form()
    sid = form.get('MessageSid') or form.get('MessageSid'.lower())
    status = form.get('MessageStatus') or form.get('MessageStatus'.lower())
    to = form.get('To')
    if not sid:
        return {"ok": False, "error": "no sid"}

    try:
        alert = await firebase_service.get_alert_by_provider_sid('twilio', sid)
        if alert:
            alert_id = alert.get('_id')
            await firebase_service.update_alert_status(alert_id, status, None)
            logger.info('Updated alert %s status=%s', alert_id, status)
        else:
            logger.info('No alert record found for sid %s', sid)
    except Exception:
        logger.exception('Error handling twilio webhook')

    return {"ok": True}
