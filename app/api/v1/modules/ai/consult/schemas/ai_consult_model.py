# app\api\v1\modules\ai\schemas\ai_consult_model.py

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal, Dict, Any


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


# ----------------------------
# Quick Action (Chips)
# ----------------------------

class AIQuickActionRequest(ORMBaseModel):
    """Request payload for chip actions: Causes / Self-care / When to see a doctor."""

    action: Literal["causes", "self_care", "red_flags"] = Field(
        ..., description="causes | self_care | red_flags"
    )
    lang: Optional[str] = Field(default=None, description="TH|EN or th-TH/en-US")


# ----------------------------
# Escalation (Handoff to Booking)
# ----------------------------

class AIConsultEscalateRequest(ORMBaseModel):
    """Create escalation/handoff payload for booking page."""

    triage_level: Optional[str] = Field(
        default=None,
        description="e.g. low|medium|high|urgent|recommended (free text)",
    )
    reason: Optional[str] = Field(
        default=None,
        description="Short summary/reason for consultation / booking prefill",
    )
    urgency: Optional[str] = Field(
        default=None,
        description="Optional UI hint: routine|soon|urgent (free text)",
    )
    note: Optional[str] = Field(default=None, description="Optional note from patient")
    lang: Optional[str] = Field(default=None, description="TH|EN or th-TH/en-US")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Extra metadata for escalation")


class AIConsultEscalatePayload(ORMBaseModel):
    escalation_id: str
    session_id: str
    company_code: str
    patient_id: Optional[str] = None

    topic_code: Optional[str] = None
    triage_level: Optional[str] = None
    reason: Optional[str] = None
    urgency: Optional[str] = None

    # for client navigation
    deeplink: Optional[str] = None
    handoff: Optional[Dict[str, Any]] = None
