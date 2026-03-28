from __future__ import annotations

from typing import Any, Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AIConsultTopicServiceItem(ORMBaseModel):
    id: UUID
    company_code: Optional[str] = None
    ai_topic_id: UUID
    service_id: UUID

    binding_type: str = "standard"
    binding_scope: str = "service"
    priority: int = 100
    sort_order: int = 0

    is_default: bool = False
    is_required: bool = False
    is_system: bool = True
    is_active: bool = True
    is_deleted: bool = False

    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    topic_code: Optional[str] = None
    topic_name_th: Optional[str] = None
    topic_name_en: Optional[str] = None
    service_code: Optional[str] = None
    service_name_th: Optional[str] = None
    service_name_en: Optional[str] = None


class AIConsultTopicServiceDetailPayload(AIConsultTopicServiceItem):
    pass


class AIConsultTopicServiceListPayload(ORMBaseModel):
    items: List[AIConsultTopicServiceItem] = Field(default_factory=list)


class AIConsultTopicServiceCreatePayload(ORMBaseModel):
    id: UUID
    company_code: Optional[str] = None
    ai_topic_id: UUID
    service_id: UUID


class AIConsultTopicServiceDeletePayload(ORMBaseModel):
    id: UUID
    deleted: bool = True