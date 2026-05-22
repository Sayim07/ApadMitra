from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from api.middleware.auth import get_current_user, require_role
from services.firebase_service import firebase_service
from services.realtime_activity_logger import realtime_activity_logger
from models.user import UserCreate, UserUpdate, UserResponse, UserRole

router = APIRouter()


class TokenVerifyRequest(BaseModel):
    id_token: str


@router.post("/auth/verify")
async def verify_token(payload: TokenVerifyRequest):
    # The token verification is handled in middleware usually,
    # but this endpoint can be used by clients to exchange token for profile
    try:
        # We will rely on firebase_admin directly via middleware helper
        from firebase_admin import auth as firebase_auth

        decoded = firebase_auth.verify_id_token(payload.id_token)
        uid = decoded.get("uid")
        if not uid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        profile = await firebase_service.get_user(uid)
        if not profile:
            profile = {
                "user_id": uid,
                "name": decoded.get("name") or "",
                "phone": decoded.get("phone_number") or "",
                "role": UserRole.CITIZEN.value,
                "preferences": {"preferred_channels": [], "preferred_language": "en"},
            }
            await firebase_service.create_user_profile(uid, profile)

        # Log the login event to Realtime Database (non-blocking)
        display_name = profile.get("name") or decoded.get("name") or decoded.get("email")
        user_role = profile.get("role", UserRole.CITIZEN.value)
        await realtime_activity_logger.log_login(
            uid=uid,
            email=decoded.get("email", ""),
            display_name=display_name,
            role=user_role,
            source="web"
        )

        return {"user": profile}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/users/me")
async def get_me(current=Depends(get_current_user)):
    profile = current.get("profile")
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")
    return profile


@router.put("/users/me")
async def update_me(update: UserUpdate, current=Depends(get_current_user)):
    uid = current.get("user_id")
    data = update.model_dump(exclude_unset=True)
    await firebase_service.create_user_profile(uid, data)
    profile = await firebase_service.get_user(uid)
    return profile


@router.get("/users/authority")
async def list_authority_users(current=Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))):
    users = await firebase_service.get_authority_contacts()
    return {"results": users}
