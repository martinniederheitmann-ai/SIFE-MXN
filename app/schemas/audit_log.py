from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity: str
    entity_id: str | None
    action: str
    actor_type: str
    actor_username: str | None
    actor_role: str | None
    is_api_key: bool
    source_path: str | None
    source_method: str | None
    before_json: str | None
    after_json: str | None
    meta_json: str | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogItem]
    total: int
    skip: int = Field(ge=0)
    limit: int = Field(ge=1)
