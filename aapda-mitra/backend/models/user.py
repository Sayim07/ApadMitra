from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserRole(str, Enum):
    CITIZEN = "CITIZEN"
    WARD_OFFICER = "WARD_OFFICER"
    RESCUE_TEAM = "RESCUE_TEAM"
    DISTRICT_AUTHORITY = "DISTRICT_AUTHORITY"
    ADMIN = "ADMIN"

class NotificationPreferences(BaseModel):
    preferred_channels: List[str] = []
    preferred_language: str = "en"
    district: Optional[str] = None

class UserCreate(BaseModel):
    user_id: str
    name: Optional[str]
    phone: Optional[str]
    role: UserRole = UserRole.CITIZEN
    preferences: Optional[NotificationPreferences] = NotificationPreferences()

class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    preferences: Optional[NotificationPreferences]

class UserResponse(BaseModel):
    user_id: str
    name: Optional[str]
    phone: Optional[str]
    role: UserRole
    preferences: NotificationPreferences
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
