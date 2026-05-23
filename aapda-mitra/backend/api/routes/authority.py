from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from api.middleware.auth import get_current_user
from services.firebase_service import firebase_service
from models.user import UserRole


router = APIRouter(prefix="/authority", tags=["authority"])


class AuthorityApplyRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    district: Optional[str] = None
    requested_role: str = Field(default=UserRole.DISTRICT_AUTHORITY.value)
    authority_types: List[str] = Field(default_factory=list)


@router.post("/apply", status_code=201)
async def apply_for_authority(payload: AuthorityApplyRequest, current=Depends(get_current_user)):
    uid = current.get("user_id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    allowed_roles = {
        UserRole.WARD_OFFICER.value,
        UserRole.RESCUE_TEAM.value,
        UserRole.DISTRICT_AUTHORITY.value,
        UserRole.ADMIN.value,
    }
    if payload.requested_role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Invalid requested_role")

    data = {
        "user_id": uid,
        "status": "PENDING",
        "requested_role": payload.requested_role,
        "authority_types": payload.authority_types or [],
        "district": payload.district,
        "name": payload.name,
        "phone": payload.phone,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        req_id = await firebase_service.create_authority_request(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"request_id": req_id, "status": "PENDING"}

