from __future__ import annotations

from typing import Any, Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AIConsultTopicCategoryItem(ORMBaseModel):
    id: UUID
    company_code: Optional[str] = None
    category_code: Optional[str] = None

    category_name_th: str
    category_name_en: str

    description_th: Optional[str] = None
    description_en: Optional[str] = None

    parent_category_id: Optional[UUID] = None
    icon_name: Optional[str] = None
    color_code: Optional[str] = None

    sort_order: int = 0
    is_active: bool = True
    is_system: bool = True
    is_deleted: bool = False

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None


class AIConsultTopicCategoryDetailPayload(AIConsultTopicCategoryItem):
    parent_category_name_th: Optional[str] = None
    parent_category_name_en: Optional[str] = None


class AIConsultTopicCategoryListPayload(ORMBaseModel):
    items: List[AIConsultTopicCategoryItem] = Field(default_factory=list)


class AIConsultTopicCategoryCreatePayload(ORMBaseModel):
    id: UUID
    company_code: Optional[str] = None
    category_code: Optional[str] = None
    category_name_th: str
    category_name_en: str


class AIConsultTopicCategoryDeletePayload(ORMBaseModel):
    id: UUID
    deleted: bool = True


#####
class AIConsultTopicCategoryOptionItem(ORMBaseModel):
    value: UUID
    label: str
    label_th: Optional[str] = None
    label_en: Optional[str] = None
    category_code: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    company_code: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class AIConsultTopicCategoryOptionsPayload(ORMBaseModel):
    items: List[AIConsultTopicCategoryOptionItem] = Field(default_factory=list)


class AIConsultTopicCategoryTreeNode(ORMBaseModel):
    id: UUID
    company_code: Optional[str] = None
    category_code: Optional[str] = None
    category_name_th: str
    category_name_en: str
    parent_category_id: Optional[UUID] = None
    icon_name: Optional[str] = None
    color_code: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    is_system: bool = True
    children: List["AIConsultTopicCategoryTreeNode"] = Field(default_factory=list)


class AIConsultTopicCategoryTreePayload(ORMBaseModel):
    items: List[AIConsultTopicCategoryTreeNode] = Field(default_factory=list)

AIConsultTopicCategoryTreeNode.model_rebuild()