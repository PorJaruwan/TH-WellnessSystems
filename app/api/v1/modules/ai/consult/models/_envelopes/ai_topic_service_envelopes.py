from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel

from app.api.v1.modules.ai.consult.models.ai_consult_topic_services_dtos import (
    AIConsultTopicServiceDetailPayload,
    AIConsultTopicServiceCreatePayload,
    AIConsultTopicServiceDeletePayload,
)


class BaseSuccessEnvelope(BaseModel):
    status: Literal["success"] = "success"
    status_code: int = 200
    message: Optional[str] = None
    data: Any


class AIConsultTopicServiceListEnvelope(BaseSuccessEnvelope):
    data: Any


class AIConsultTopicServiceDetailEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicServiceDetailPayload


class AIConsultTopicServiceCreateEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicServiceCreatePayload


class AIConsultTopicServiceUpdateEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicServiceDetailPayload


class AIConsultTopicServiceDeleteEnvelope(BaseSuccessEnvelope):
    data: AIConsultTopicServiceDeletePayload