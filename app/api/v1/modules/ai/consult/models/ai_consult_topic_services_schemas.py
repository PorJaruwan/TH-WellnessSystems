from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.api.v1.modules.ai.consult.models.ai_consult_topic_services_dtos import ORMBaseModel


class CreateAIConsultTopicServiceRequest(ORMBaseModel):
    ai_topic_id: UUID
    service_id: UUID

    binding_type: str = Field(default="standard", max_length=50)
    binding_scope: str = Field(default="service", max_length=50)
    priority: int = Field(default=100)
    sort_order: int = Field(default=0)

    is_default: bool = Field(default=False)
    is_required: bool = Field(default=False)
    is_system: bool = Field(default=True)
    is_active: bool = Field(default=True)

    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateAIConsultTopicServiceRequest(ORMBaseModel):
    binding_type: Optional[str] = Field(default=None, max_length=50)
    binding_scope: Optional[str] = Field(default=None, max_length=50)
    priority: Optional[int] = None
    sort_order: Optional[int] = None

    is_default: Optional[bool] = None
    is_required: Optional[bool] = None
    is_system: Optional[bool] = None
    is_active: Optional[bool] = None

    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None