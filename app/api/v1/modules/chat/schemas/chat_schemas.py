# app/api/v1/modules/chat/schemas/chat_schemas.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ChatSessionHeaderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    topic: Optional[str] = None  # topic_code or resolved label (ถ้ามี layer แปลง)
    triage_level: Optional[str] = None
    triage_reason: Optional[str] = None
    last_activity_at: Optional[datetime] = None
    status: Optional[str] = None


class ChatMessageItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID

    role: Literal["user", "assistant", "system"] = "user"
    content_text: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None

    created_at: datetime


class ChatMessagesListResponse(BaseModel):
    items: List[ChatMessageItem]
    limit: int
    before: Optional[datetime] = None


class ChatMessageCreateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


class TriageInfo(BaseModel):
    level: Optional[str] = None
    reason: Optional[str] = None


class UiCard(BaseModel):
    # ใช้ได้ทั้ง chip/cta/card ตาม UI ของคุณ
    type: Literal["chip", "cta", "card"] = "chip"
    label: str
    value: Optional[str] = None
    action: Optional[Dict[str, Any]] = None


class RetrievalInfo(BaseModel):
    provider: Optional[str] = None
    top_k: Optional[int] = None
    chunks: Optional[List[Dict[str, Any]]] = None


class ChatMessageCreateResponse(BaseModel):
    assistant_text: str
    triage: TriageInfo = Field(default_factory=TriageInfo)
    ui_cards: List[UiCard] = Field(default_factory=list)
    retrieval: Optional[RetrievalInfo] = None
