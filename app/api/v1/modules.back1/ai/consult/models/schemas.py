from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field

from .dtos import ORMBaseModel


class CreateAIConsultSessionRequest(ORMBaseModel):
    topic_code: str = Field(..., min_length=1, description="Topic code from ai_topics")
    language: Optional[str] = Field(default="th-TH", description="th-TH/en-US or TH/EN")
    entry_point: Optional[str] = Field(default="pre_consult", description="e.g. pre_consult, homepage_free_ai")


class AIQuickActionRequest(ORMBaseModel):
    """Request payload for chip actions: Causes / Self-care / When to see a doctor."""
    action: Literal["cause", "self_care", "red_flag"] = Field(
        ..., description="cause | self_care | red_flag"
    )
    lang: Optional[str] = Field(default=None, description="TH|EN or th-TH/en-US")


class AIConsultEscalateRequest(ORMBaseModel):
    """Create escalation/handoff payload for booking page."""
