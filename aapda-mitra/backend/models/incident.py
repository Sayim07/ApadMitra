from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DisasterType(str, Enum):
    FLOOD = "FLOOD"
    CYCLONE = "CYCLONE"
    EARTHQUAKE = "EARTHQUAKE"
    LANDSLIDE = "LANDSLIDE"
    WILDFIRE = "WILDFIRE"
    OTHER = "OTHER"

class SourceType(str, Enum):
    CITIZEN_REPORT = "CITIZEN_REPORT"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    WEATHER_API = "WEATHER_API"
    NEWS_FEED = "NEWS_FEED"

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    SUSPICIOUS = "SUSPICIOUS"
    FAKE = "FAKE"

class SeverityLevel(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    UNASSIGNED = "UNASSIGNED"

class IncidentCreate(BaseModel):
    disaster_type: DisasterType
    source_type: SourceType
    raw_text: str
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    media_urls: Optional[List[str]] = []

class IncidentUpdate(BaseModel):
    verification_score: Optional[int]
    verification_status: Optional[VerificationStatus]
    severity: Optional[SeverityLevel]
    priority_score: Optional[int]
    alerts_sent: Optional[List[str]]
    channels_dispatched: Optional[List[str]]
    acknowledged_by: Optional[List[str]]

class IncidentResponse(BaseModel):
    incident_id: str
    disaster_type: DisasterType
    source_type: SourceType
    raw_text: str
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    verification_score: int
    verification_status: VerificationStatus
    severity: SeverityLevel
    priority_score: int
    alerts_sent: List[str]
    channels_dispatched: List[str]
    acknowledged_by: List[str]
    media_urls: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
