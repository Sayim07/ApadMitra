from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import asyncio

from services.firebase_service import firebase_service
from services.realtime_activity_logger import realtime_activity_logger
from services.notification_service import SMSService, EmailService
from config.settings import settings
from services.cloudinary_service import cloudinary_service
from utils.retry_queue import AsyncRetry
from services.notification_queue import notification_queue
try:
    from api.routes.metrics import INCIDENTS_CREATED
except Exception:
    INCIDENTS_CREATED = None
from models.incident import IncidentCreate, IncidentResponse, SeverityLevel, VerificationStatus, DisasterType
from api.middleware.auth import require_role, get_current_user
from models.user import UserRole
try:
    from agents.pipeline import pipeline
except Exception:
    pipeline = None

router = APIRouter(prefix="/incidents")


class AcknowledgeRequest(BaseModel):
    acknowledged_by: Optional[str]


class FollowUpCreate(BaseModel):
    raw_text: str
    authority_type: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    disaster_type: Optional[str] = None


@router.post("", status_code=201)
async def submit_incident(request: Request):
    """
    Accept either JSON body (legacy) or multipart/form-data with files.
    If multipart, files are uploaded to Cloudinary and the incident document is
    updated with `media_urls` (secure HTTPS URLs).
    """
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()

        # Parse standard fields from the form
        disaster_type = form.get("disaster_type") or DisasterType.OTHER.value
        source_type = form.get("source_type") or "CITIZEN_REPORT"
        raw_text = form.get("raw_text") or ""
        location_name = form.get("location_name")
        latitude = form.get("latitude")
        longitude = form.get("longitude")
        target_authority_types_raw = form.get("target_authority_types")
        target_authority_types: List[str] = []
        if target_authority_types_raw:
            parts = [p.strip() for p in str(target_authority_types_raw).split(",")]
            target_authority_types = [p.upper() for p in parts if p]

        data = {
            "disaster_type": disaster_type,
            "source_type": source_type,
            "raw_text": raw_text,
            "location_name": location_name,
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "verification_score": 0,
            "verification_status": VerificationStatus.PENDING.value,
            "severity": SeverityLevel.UNASSIGNED.value,
            "priority_score": 0,
            "alerts_sent": [],
            "channels_dispatched": [],
            "acknowledged_by": [],
            "media_urls": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "report_kind": "PRIMARY",
            "routing_status": "ROUTED" if target_authority_types else None,
            "target_authority_types": target_authority_types,
        }

        incident_id = await firebase_service.create_incident(data)
        try:
            if INCIDENTS_CREATED is not None:
                INCIDENTS_CREATED.inc()
        except Exception:
            pass

        # enqueue for pipeline processing
        try:
            if pipeline is not None:
                await pipeline.enqueue_incident(incident_id)
        except Exception:
            pass

        # handle files
        async def handle_incident_media(files: list[UploadFile], incident_id: str) -> list[str]:
            media_urls: list[str] = []
            allowed_types = ["image/jpeg", "image/png", "image/webp", "video/mp4", "video/quicktime"]
            for file in files:
                if file and getattr(file, "filename", None):
                    file_bytes = await file.read()
                    # Validate file size (max 10MB)
                    if len(file_bytes) > 10 * 1024 * 1024:
                        raise HTTPException(status_code=400, detail="File too large. Max 10MB per file.")
                    # Validate file type
                    if file.content_type not in allowed_types:
                        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
                    result = await cloudinary_service.upload_incident_media(
                        file_bytes,
                        file.filename,
                        incident_id
                    )
                    media_urls.append(result["secure_url"])
            return media_urls

        files = []
        # form may contain multiple 'files'
        for key, val in form.multi_items():
            if key == "files" and isinstance(val, UploadFile):
                files.append(val)

        if files:
            media_urls = await handle_incident_media(files, incident_id)
            await firebase_service.update_incident(incident_id, {"media_urls": media_urls, "updated_at": datetime.utcnow()})
            # Log each media upload to Realtime Database (non-blocking)
            for idx, url in enumerate(media_urls):
                if idx < len(files):
                    file = files[idx]
                    await realtime_activity_logger.log_upload(
                        user_id="anonymous",
                        incident_id=incident_id,
                        file_name=file.filename or f"file_{idx}",
                        file_url=url,
                        file_type=file.content_type or "application/octet-stream"
                    )

        # Log incident submission to Realtime Database (non-blocking)
        await realtime_activity_logger.log_incident_submission(
            incident_id=incident_id,
            status=VerificationStatus.PENDING.value,
            severity=SeverityLevel.UNASSIGNED.value,
            disaster_type=data.get("disaster_type"),
            location={"latitude": data.get("latitude"), "longitude": data.get("longitude"), "name": data.get("location_name")} if data.get("latitude") and data.get("longitude") else None
        )

        return {"incident_id": incident_id}
    else:
        # JSON body
        payload = await request.json()
        data = payload
        target_authority_types = data.get("target_authority_types") or []
        if isinstance(target_authority_types, str):
            target_authority_types = [p.strip().upper() for p in target_authority_types.split(",") if p.strip()]
        if isinstance(target_authority_types, list):
            data["target_authority_types"] = [str(x).upper() for x in target_authority_types if x]
        data.update({
            "verification_score": 0,
            "verification_status": VerificationStatus.PENDING.value,
            "severity": SeverityLevel.UNASSIGNED.value,
            "priority_score": 0,
            "alerts_sent": [],
            "channels_dispatched": [],
            "acknowledged_by": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "report_kind": data.get("report_kind") or "PRIMARY",
        })
        incident_id = await firebase_service.create_incident(data)
        try:
            if pipeline is not None:
                await pipeline.enqueue_incident(incident_id)
        except Exception:
            pass
        return {"incident_id": incident_id}


@router.post("/sos", status_code=201)
async def submit_sos(request: Request):
    body = await request.json()
    target_authority_types = body.get("target_authority_types") or []
    if isinstance(target_authority_types, str):
        target_authority_types = [p.strip().upper() for p in target_authority_types.split(",") if p.strip()]
    if isinstance(target_authority_types, list):
        target_authority_types = [str(x).upper() for x in target_authority_types if x]
    data = {
        "disaster_type": body.get("disaster_type", DisasterType.OTHER.value),
        "source_type": body.get("source_type", "CITIZEN_REPORT"),
        "raw_text": body.get("raw_text", "SOS - Citizen in distress"),
        "location_name": body.get("location_name"),
        "latitude": body.get("latitude"),
        "longitude": body.get("longitude"),
        "verification_score": 0,
        "verification_status": VerificationStatus.PENDING.value,
        "severity": SeverityLevel.UNASSIGNED.value,
        "priority_score": 100,
        "alerts_sent": [],
        "channels_dispatched": [],
        "acknowledged_by": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "report_kind": "PRIMARY",
        "routing_status": "ROUTED" if target_authority_types else None,
        "target_authority_types": target_authority_types,
    }
    incident_id = await firebase_service.create_incident(data)
    try:
        if pipeline is not None:
            await pipeline.enqueue_incident(incident_id)
    except Exception:
        pass
    return {"incident_id": incident_id}


@router.get("")
async def list_incidents(
    severity: Optional[str] = None,
    verification_status: Optional[str] = None,
    disaster_type: Optional[str] = None,
    district: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current=Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN)),
):
    filters = {}
    if severity:
        filters["severity"] = severity
    if verification_status:
        filters["verification_status"] = verification_status
    if disaster_type:
        filters["disaster_type"] = disaster_type
    if district:
        filters["district"] = district

    incidents = await firebase_service.get_incidents(filters=filters, limit=limit)
    prefs = (current.get("profile") or {}).get("preferences") or {}
    authority_types = prefs.get("authority_types") or []
    authority_types = [str(x).upper() for x in authority_types if x]
    if not authority_types:
        return {"results": incidents}

    wanted = set(authority_types)
    mapping = {
        "FLOOD": ["FLOOD"],
        "FIRE": ["FIRE"],
        "EARTHQUAKE": ["EARTHQUAKE"],
        "CYCLONE": ["CYCLONE"],
        "LANDSLIDE": ["LANDSLIDE"],
        "ROAD_DAMAGE": ["ROAD_DAMAGE"],
        "TREE_FALL": ["TREE_FALL"],
        "ELECTRICITY": ["ELECTRICITY"],
        "MEDICAL": ["MEDICAL"],
    }

    filtered = []
    for inc in incidents:
        targets = inc.get("target_authority_types") or []
        targets = [str(x).upper() for x in targets if x]
        if not targets:
            dt = str(inc.get("disaster_type") or "GENERAL").upper()
            targets = mapping.get(dt, ["GENERAL"])
        if set(targets).intersection(wanted):
            filtered.append(inc)

    return {"results": filtered}


@router.get("/active")
async def get_active(current=Depends(require_role(UserRole.WARD_OFFICER, UserRole.RESCUE_TEAM, UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))):
    incidents = await firebase_service.get_active_incidents()
    prefs = (current.get("profile") or {}).get("preferences") or {}
    authority_types = prefs.get("authority_types") or []
    authority_types = [str(x).upper() for x in authority_types if x]
    if not authority_types:
        return {"results": incidents}

    wanted = set(authority_types)
    mapping = {
        "FLOOD": ["FLOOD"],
        "FIRE": ["FIRE"],
        "EARTHQUAKE": ["EARTHQUAKE"],
        "CYCLONE": ["CYCLONE"],
        "LANDSLIDE": ["LANDSLIDE"],
        "ROAD_DAMAGE": ["ROAD_DAMAGE"],
        "TREE_FALL": ["TREE_FALL"],
        "ELECTRICITY": ["ELECTRICITY"],
        "MEDICAL": ["MEDICAL"],
    }

    filtered = []
    for inc in incidents:
        targets = inc.get("target_authority_types") or []
        targets = [str(x).upper() for x in targets if x]
        if not targets:
            dt = str(inc.get("disaster_type") or "GENERAL").upper()
            targets = mapping.get(dt, ["GENERAL"])
        if set(targets).intersection(wanted):
            filtered.append(inc)

    return {"results": filtered}


@router.get("/{incident_id}")
async def get_incident(incident_id: str, current=Depends(get_current_user)):
    incident = await firebase_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.put("/{incident_id}/acknowledge", dependencies=[Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def acknowledge_incident(incident_id: str, payload: AcknowledgeRequest):
    updates = {"acknowledged": True, "acknowledged_by": payload.acknowledged_by or [] , "updated_at": datetime.utcnow()}
    await firebase_service.update_incident(incident_id, updates)
    # record action
    try:
        await firebase_service.create_incident_action(incident_id, {"action": "acknowledge", "by": payload.acknowledged_by or [], "ts": datetime.utcnow()})
    except Exception:
        pass
    return {"ok": True}


@router.post("/{incident_id}/assign", dependencies=[Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def assign_incident(incident_id: str, body: dict):
    # body: {"team_id": "...", "notes": "..."}
    updates = {"assigned_to": body, "updated_at": datetime.utcnow()}
    await firebase_service.update_incident(incident_id, updates)
    try:
        await firebase_service.create_incident_action(incident_id, {"action": "assign", "by": "authority", "details": body, "ts": datetime.utcnow()})
    except Exception:
        pass
    # notify assigned team contacts and create alert record
    try:
        team_id = body.get('team_id')
        team = None
        if team_id:
            team = await firebase_service.get_team(team_id)
        message = f"Incident {incident_id} assigned to {team_id}. Notes: {body.get('notes', '')}"
        # create alert record
        alert_data = {"incident_id": incident_id, "provider": "SYSTEM", "provider_sid": None, "message": message, "delivery_status": "PENDING", "created_at": datetime.utcnow()}
        try:
            alert_id = await firebase_service.create_alert(alert_data)
        except Exception:
            alert_id = None

        contacts = team.get('contacts', []) if team else []

        # Enqueue a notification job per contact for persistence + retry
        for c in contacts:
            try:
                if c.get('phone'):
                    item = {
                        "alert_id": alert_id,
                        "incident_id": incident_id,
                        "channel": "sms",
                        "to": c.get('phone'),
                        "message": message,
                    }
                    # schedule enqueue (fire-and-forget)
                    try:
                        asyncio.create_task(notification_queue.enqueue(item))
                    except Exception:
                        # fallback to await if create_task unavailable
                        await notification_queue.enqueue(item)
                if c.get('email'):
                    item = {
                        "alert_id": alert_id,
                        "incident_id": incident_id,
                        "channel": "email",
                        "to": c.get('email'),
                        "subject": f"Assigned: Incident {incident_id}",
                        "html": message,
                    }
                    try:
                        asyncio.create_task(notification_queue.enqueue(item))
                    except Exception:
                        await notification_queue.enqueue(item)
            except Exception:
                # don't let notification failures block assign
                logger = None

    except Exception:
        pass

    return {"ok": True}


@router.post("/{incident_id}/dispatch", dependencies=[Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def dispatch_incident(incident_id: str):
    # Trigger immediate dispatch for an incident (authority-initiated)
    try:
        from agents.dispatch_agent import DispatchAgent
        disp = DispatchAgent()
        result = await disp.dispatch_all(incident_id)
        try:
            await firebase_service.create_incident_action(incident_id, {"action": "dispatch", "by": "authority", "result": {"attempted": result.channels_attempted, "succeeded": result.channels_succeeded, "failed": result.channels_failed, "alert_ids": result.alert_ids}, "ts": datetime.utcnow()})
        except Exception:
            pass
        return {"ok": True, "result": {"attempted": result.channels_attempted, "succeeded": result.channels_succeeded, "failed": result.channels_failed, "alert_ids": result.alert_ids}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{incident_id}/followup", status_code=201, dependencies=[Depends(require_role(UserRole.WARD_OFFICER, UserRole.RESCUE_TEAM, UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def create_followup(incident_id: str, payload: FollowUpCreate, current=Depends(get_current_user)):
    parent = await firebase_service.get_incident(incident_id)
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    authority_type = (payload.authority_type or "").strip().upper() or None
    disaster_type = (payload.disaster_type or authority_type or parent.get("disaster_type") or DisasterType.OTHER.value)

    data = {
        "disaster_type": disaster_type,
        "source_type": "AUTHORITY_REPORT",
        "raw_text": payload.raw_text,
        "location_name": payload.location_name or parent.get("location_name"),
        "latitude": payload.latitude if payload.latitude is not None else parent.get("latitude"),
        "longitude": payload.longitude if payload.longitude is not None else parent.get("longitude"),
        "verification_score": 0,
        "verification_status": VerificationStatus.PENDING.value,
        "severity": SeverityLevel.UNASSIGNED.value,
        "priority_score": 0,
        "alerts_sent": [],
        "channels_dispatched": [],
        "acknowledged_by": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "report_kind": "FOLLOW_UP",
        "parent_incident_id": incident_id,
        "reported_by_user_id": current.get("user_id"),
        "reported_by_role": current.get("role"),
        "routing_status": "PENDING",
        "target_authority_types": [authority_type] if authority_type else [],
    }

    followup_id = await firebase_service.create_incident(data)
    try:
        await firebase_service.create_incident_action(incident_id, {"action": "followup_created", "by": current.get("user_id"), "details": {"followup_id": followup_id}, "ts": datetime.utcnow()})
    except Exception:
        pass

    try:
        await firebase_service.create_incident_action(followup_id, {"action": "created", "by": current.get("user_id"), "details": {"parent_incident_id": incident_id}, "ts": datetime.utcnow()})
    except Exception:
        pass

    return {"incident_id": followup_id}


@router.get("/{incident_id}/actions", dependencies=[Depends(get_current_user)])
async def get_incident_actions(incident_id: str, limit: int = 100):
    try:
        actions = await firebase_service.get_incident_actions(incident_id, limit=limit)
        return {"results": actions}
    except Exception:
        # fallback empty
        return {"results": []}
