from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import Field

from .dtos import ORMBaseModel


class CreateAIConsultSessionRequest(ORMBaseModel):
    topic_code: str = Field(..., min_length=1, description="Topic code from ai_topics")
    language: Optional[str] = Field(default="th-TH", description="th-TH/en-US or TH/EN")
    entry_point: Optional[str] = Field(default="pre_consult", description="e.g. pre_consult, homepage_free_ai")


class SearchAITopicsRequest(ORMBaseModel):
    lang: Optional[str] = Field(default=None, description="TH|EN or th-TH/en-US")
    category_id: Optional[UUID] = Field(default=None)
    q: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=True)
    include_uncategorized: bool = Field(default=True)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="sort_order")
    sort_dir: Literal["asc", "desc"] = Field(default="asc")


class AIQuickActionRequest(ORMBaseModel):
    action: Literal["cause", "self_care", "red_flag"] = Field(
        ..., description="cause | self_care | red_flag"
    )
    lang: Optional[str] = Field(default=None, description="TH|EN or th-TH/en-US")


class AIConsultEscalateRequest(ORMBaseModel):
    """Create escalation/handoff payload for booking page."""