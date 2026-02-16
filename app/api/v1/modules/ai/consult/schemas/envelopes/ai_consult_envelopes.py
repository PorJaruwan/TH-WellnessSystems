# app\api\v1\modules\ai\schemas\envelopes\ai_consult_envelopes.py

from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, Literal, Any

from app.api.v1.modules.ai.consult.schemas.ai_consult_model import (
    AITopicsList,
    AITopicCardsPayload,
    CreateAIConsultSessionPayload,
    AIConsultEscalatePayload,
)


class BaseSuccessEnvelope(BaseModel):
    status: Literal["success"] = "success"
    status_code: int = 200
    message: Optional[str] = None
    data: Any


class AITopicsEnvelope(BaseSuccessEnvelope):
    data: AITopicsList


class AITopicCardsEnvelope(BaseSuccessEnvelope):
    data: AITopicCardsPayload


class AIConsultSessionEnvelope(BaseSuccessEnvelope):
    data: CreateAIConsultSessionPayload


class AIConsultEscalateEnvelope(BaseSuccessEnvelope):
    data: AIConsultEscalatePayload
