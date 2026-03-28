from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel

from app.api.v1.modules.ai.consult.models.ai_consult_topic_categories_dtos import (
    AIConsultTopicCategoryDetailPayload,
    AIConsultTopicCategoryCreatePayload,
    AIConsultTopicCategoryDeletePayload,
    AIConsultTopicCategoryOptionsPayload,
    AIConsultTopicCategoryTreePayload,
)


class BaseSuccessEnvelope(BaseModel):
    status: Literal["success"] = "success"
    status_code: int = 200
    message: Optional[str] = None
    data: Any


class AIConsultTopicCategoryListEnvelope(BaseSuccessEnvelope):
    data: Any


class AIConsultTopicCategoryDetailEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicCategoryDetailPayload


class AIConsultTopicCategoryCreateEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicCategoryCreatePayload


class AIConsultTopicCategoryUpdateEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicCategoryDetailPayload


class AIConsultTopicCategoryDeleteEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicCategoryDeletePayload


class AIConsultTopicCategoryOptionsEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicCategoryOptionsPayload


class AIConsultTopicCategoryTreeEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicCategoryTreePayload