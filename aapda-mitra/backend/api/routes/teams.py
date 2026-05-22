from fastapi import APIRouter, Depends
from typing import Optional

from services.firebase_service import firebase_service
from api.middleware.auth import require_role
from models.user import UserRole

router = APIRouter()


@router.get('/teams', dependencies=[Depends(require_role(UserRole.DISTRICT_AUTHORITY, UserRole.ADMIN))])
async def list_teams(district: Optional[str] = None):
    teams = []
    try:
        teams = await firebase_service.get_teams(district=district)
    except Exception:
        # fallback sample teams
        teams = [
            {"team_id": "team-1", "name": "Rescue Team Alpha", "district": district or "Default"},
            {"team_id": "team-2", "name": "Medical Team Beta", "district": district or "Default"},
        ]
    return {"results": teams}
