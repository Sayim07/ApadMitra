from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging
from typing import Optional, Callable

try:
    from firebase_admin import auth as firebase_auth
except Exception:
    firebase_auth = None
from services.firebase_service import firebase_service
from models.user import UserRole

logger = logging.getLogger("auth_middleware")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/verify")


def verify_firebase_token(token: str) -> dict:
    # If firebase_admin is not available (tests/local), allow a simple test token
    if firebase_auth is None:
        if token == "test" or token == "":
            return {"uid": "testuser", "name": "Test User", "phone_number": "+10000000000"}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials - no firebase")

    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception as e:
        logger.exception("Invalid Firebase token: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    claims = verify_firebase_token(token)
    uid = claims.get("uid")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing uid")

    user = await firebase_service.get_user(uid)
    if not user:
        # create a minimal profile
        profile = {
            "user_id": uid,
            "name": claims.get("name") or "",
            "phone": claims.get("phone_number") or "",
            "role": UserRole.CITIZEN.value,
            "preferences": {"preferred_channels": [], "preferred_language": "en"},
        }
        await firebase_service.create_user_profile(uid, profile)
        user = profile

    return {"user_id": uid, "role": user.get("role"), "district": user.get("preferences", {}).get("district"), "profile": user}


def require_role(*roles: UserRole) -> Callable:
    allowed = [r.value if isinstance(r, UserRole) else str(r) for r in roles]

    async def _dependency(current=Depends(get_current_user)):
        user_role = current.get("role")
        if user_role is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not found")

        # role hierarchy
        hierarchy = [
            UserRole.CITIZEN.value,
            UserRole.WARD_OFFICER.value,
            UserRole.RESCUE_TEAM.value,
            UserRole.DISTRICT_AUTHORITY.value,
            UserRole.ADMIN.value,
        ]

        def rank(r):
            try:
                return hierarchy.index(r)
            except ValueError:
                return 0

        user_rank = rank(user_role)
        # if any allowed role has rank >= user_rank, permit
        for a in allowed:
            if user_rank >= rank(a):
                return current

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    return _dependency
