from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import List, Dict
from services.firebase_service import firebase_service
from api.middleware.auth import require_role
from models.user import UserRole

router = APIRouter(prefix="/dashboard")


@router.get("/summary", dependencies=[Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def summary():
    # Basic summary aggregation (placeholder)
    active = await firebase_service.get_active_incidents()
    total_active = len(active)
    by_severity = {"red": sum(1 for i in active if i.get("severity") == "RED"), "yellow": sum(1 for i in active if i.get("severity") == "YELLOW"), "green": sum(1 for i in active if i.get("severity") == "GREEN")}
    by_type = {}
    for i in active:
        t = i.get("disaster_type", "OTHER")
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "total_active": total_active,
        "by_severity": by_severity,
        "by_type": by_type,
        "avg_response_time_minutes": 0.0,
        "verification_stats": {"verified": 0, "suspicious": 0, "fake": 0},
        "alerts_sent_today": 0,
        "acknowledgment_rate": 0.0,
    }


@router.get("/heatmap", dependencies=[Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def heatmap():
    # placeholder: return empty list
    return {"points": []}


@router.get("/incidents/stream", dependencies=[Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def incidents_stream():
    async def event_generator():
        last = None
        while True:
            try:
                active = await firebase_service.get_active_incidents()
                payload = json.dumps(active)
                if payload != last:
                    last = payload
                    yield f"data: {payload}\n\n"
            except Exception:
                yield f"data: []\n\n"
            await asyncio.sleep(3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/alerts/recent", dependencies=[Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def recent_alerts():
    # placeholder: return empty
    return {"results": []}
