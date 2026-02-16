# app/api/v1/modules/chat/schemas/chat_model.py

from __future__ import annotations
from datetime import datetime
from typing import Any, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field


class ChatSessionHeaderPayload(BaseModel):
    session_id: UUID
    topic: Optional[str] = None
    triage_level: Optional[str] = None
    triage_reason: Optional[str] = None
    last_activity_at: Optional[datetime] = None
    status: Optional[str] = None


class ChatMessageItem(BaseModel):
    id: UUID
    session_id: UUID
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    content_json: dict[str, Any] = {}
    created_at: datetime


class ChatSendMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


class TriagePayload(BaseModel):
    level: Optional[str] = None
    reason: Optional[str] = None


class ChatSendMessagePayload(BaseModel):
    assistant_text: str
    triage: TriagePayload = TriagePayload()
    ui_cards: list[dict[str, Any]] = []
    retrieval: Optional[dict[str, Any]] = None
