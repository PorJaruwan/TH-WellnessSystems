# app\api\v1\modules\ai\schemas\ai_consult_model.py

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AITopicItem(ORMBaseModel):
    topic_code: str
    label: str
    description: Optional[str] = None
    sort_order: int = 0


class AITopicsList(ORMBaseModel):
    items: List[AITopicItem] = Field(default_factory=list)


class AITopicCards(ORMBaseModel):
    causes: List[str] = Field(default_factory=list)
    self_care: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)


class AITopicCardsPayload(ORMBaseModel):
    topic_code: str
    cards: AITopicCards
    disclaimer: str


# ----------------------------
# AI Consult Session (Create/Re-use)
# ----------------------------
class CreateAIConsultSessionRequest(ORMBaseModel):
    topic_code: str = Field(..., min_length=1, description="Topic code from ai_topics")
    language: Optional[str] = Field(default="th-TH", description="th-TH/en-US or TH/EN")
    entry_point: Optional[str] = Field(default="pre_consult", description="e.g. pre_consult, homepage_free_ai")


class CreateAIConsultSessionPayload(ORMBaseModel):
    session_id: str
    company_code: str
    patient_id: str

    topic_code: str
    language: str
    entry_point: str

    app_context: str
    channel: str
    status: str

    # ✅ for client to know whether it re-used an existing active session
    is_reused: bool = False
