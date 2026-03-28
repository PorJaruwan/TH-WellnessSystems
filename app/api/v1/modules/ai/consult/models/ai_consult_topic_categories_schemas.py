from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.api.v1.modules.ai.consult.models.ai_consult_topic_categories_dtos import ORMBaseModel


class CreateAIConsultTopicCategoryRequest(ORMBaseModel):
    category_code: Optional[str] = Field(default=None, max_length=100)
    category_name_th: str = Field(..., min_length=1, max_length=255)
    category_name_en: str = Field(..., min_length=1, max_length=255)

    description_th: Optional[str] = None
    description_en: Optional[str] = None

    parent_category_id: Optional[UUID] = None
    icon_name: Optional[str] = Field(default=None, max_length=100)
    color_code: Optional[str] = Field(default=None, max_length=30)

    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    is_system: bool = Field(default=True)

    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateAIConsultTopicCategoryRequest(ORMBaseModel):
    category_code: Optional[str] = Field(default=None, max_length=100)
    category_name_th: Optional[str] = Field(default=None, min_length=1, max_length=255)
    category_name_en: Optional[str] = Field(default=None, min_length=1, max_length=255)

    description_th: Optional[str] = None
    description_en: Optional[str] = None

    parent_category_id: Optional[UUID] = None
    icon_name: Optional[str] = Field(default=None, max_length=100)
    color_code: Optional[str] = Field(default=None, max_length=30)

    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    is_system: Optional[bool] = None
    metadata: Optional[dict[str, Any]] = None