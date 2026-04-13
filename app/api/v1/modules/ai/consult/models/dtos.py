from __future__ import annotations

from typing import List, Optional, Any

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AITopicItem(ORMBaseModel):
    id: Optional[str] = None
    company_code: Optional[str] = None
    topic_code: str
    label: str
    description: Optional[str] = None
    sort_order: int = 0

    category_id: Optional[str] = None
    category_code: Optional[str] = None
    category_name: Optional[str] = None
    parent_category_id: Optional[str] = None

    topic_type: Optional[str] = None
    topic_level: Optional[str] = None
    intent_code: Optional[str] = None
    output_format: Optional[str] = None
    action_type: Optional[str] = None

    requires_auth: bool = False
    requires_patient_context: bool = False
    requires_booking_context: bool = False
    requires_payment_context: bool = False
    requires_service_context: bool = False

    is_active: bool = True
    is_system: bool = True
    is_default: bool = False
    version_no: int = 1

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AITopicsList(ORMBaseModel):
    items: List[AITopicItem] = Field(default_factory=list)


class AITopicCards(ORMBaseModel):
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