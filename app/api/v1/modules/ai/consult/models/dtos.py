from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    # ✅ order for UI: 1) check 2) self_care 3) red_flag 4) cause
    check: List[str] = Field(default_factory=list)
    self_care: List[str] = Field(default_factory=list)
    red_flag: List[str] = Field(default_factory=list)
    cause: List[str] = Field(default_factory=list)


class AITopicCardsPayload(ORMBaseModel):
    topic_code: str
    cards: AITopicCards
    disclaimer: str


class AIConsultSessionItem(ORMBaseModel):
    session_id: str
    company_code: str
    patient_id: Optional[str] = None
    topic_code: Optional[str] = None
    language: Optional[str] = None
    status: str
    last_activity_at: Optional[str] = None
    created_at: Optional[str] = None
    entry_point: Optional[str] = None


class AIConsultSessionsListPayload(ORMBaseModel):
    items: List[AIConsultSessionItem] = Field(default_factory=list)


class AIConsultSessionDetailPayload(AIConsultSessionItem):
    staff_id: Optional[str] = None
    triage_level: Optional[str] = None
    triage_reason: Optional[str] = None
    app_context: Optional[str] = None
    channel: Optional[str] = None

class CreateAIConsultSessionPayload(ORMBaseModel):
    session_id: str
    company_code: str
    patient_id: str


class AIConsultEscalatePayload(ORMBaseModel):
    escalation_id: str
    session_id: str
    company_code: str
    patient_id: Optional[str] = None