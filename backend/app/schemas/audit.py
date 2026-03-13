from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.audit import AuditActionType, AuthEventType


class AuditLogOut(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    action_type: AuditActionType
    entity_type: str
    entity_id: Optional[str]
    entity_version_id: Optional[int]
    old_data_json: Optional[dict]
    new_data_json: Optional[dict]
    changed_fields_json: Optional[list]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    event_type: AuthEventType
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditFilterParams(BaseModel):
    action_type: Optional[AuditActionType] = None
    entity_type: Optional[str] = None
    user_id: Optional[int] = None
    page: int = 1
    size: int = 50
