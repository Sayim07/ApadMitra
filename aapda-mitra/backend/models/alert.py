from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChannelType(str, Enum):
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    VOICE = "VOICE"
    DASHBOARD = "DASHBOARD"
    API = "API"

class DeliveryStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"

class TargetAudience(str, Enum):
    CITIZEN = "CITIZEN"
    AUTHORITY = "AUTHORITY"
    STATE = "STATE"

class AlertCreate(BaseModel):
    incident_id: str
    channel: ChannelType
    language: Optional[str] = "en"
    content_text: str
    content_html: Optional[str]

class AlertUpdate(BaseModel):
    delivery_status: Optional[DeliveryStatus]
    delivered_at: Optional[datetime]

class AlertResponse(BaseModel):
    alert_id: str
    incident_id: str
    channel: ChannelType
    language: Optional[str]
    content_text: str
    content_html: Optional[str]
    delivery_status: DeliveryStatus
    created_at: datetime

    model_config = {"from_attributes": True}
