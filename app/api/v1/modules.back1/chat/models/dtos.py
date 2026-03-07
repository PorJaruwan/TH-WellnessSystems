from __future__ import annotations

"""Response DTO models (Outbound) for Chat module.

WellPlus API Module Standard:
- dtos.py MUST contain Response models only.
- Request models MUST be in schemas.py.
"""

from datetime import datetime

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


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
    role: str
    content: str
    content_json: dict[str, Any] = {}
    created_at: datetime


class ChatSendMessagePayload(BaseModel):
    assistant_text: str
    triage: dict[str, Any] = {}
    ui_cards: list[dict[str, Any]] = []
    retrieval: Optional[dict[str, Any]] = None


class ChatCreateSessionPayload(BaseModel):
    session_id: UUID
    status: str
    topic_code: Optional[str] = None
    language: Optional[str] = None
    last_activity_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class ChatSessionSummaryItem(BaseModel):
    session_id: UUID
    status: str
    last_activity_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    title: Optional[str] = None
    topic_code: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message: Optional[str] = None


class ChatSoftDeleteMessagePayload(BaseModel):
    message_id: UUID
    deleted: bool


class ChatCitationItem(BaseModel):
    chunk_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    doc_title: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    score: Optional[float] = None
    snippet: Optional[str] = None
    raw: dict[str, Any] = {}


class ChatCitationsPayload(BaseModel):
    assistant_message_id: UUID
    citations: list[ChatCitationItem]


# -------------------------
# Retrievals
# -------------------------

class ChatRetrievalItemOut(BaseModel):
    id: UUID
    retrieval_id: UUID
    chunk_id: UUID
    document_id: Optional[UUID] = None
    rank: int
    score: float
    metadata: dict[str, Any]
    created_at: datetime


class ChatRetrievalOut(BaseModel):
    id: UUID
    company_code: str
    session_id: UUID
    assistant_message_id: Optional[UUID] = None
    query_text: Optional[str] = None
    query_hash: Optional[str] = None
    top_k: int
    filters: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime


class ChatRetrievalDetailOut(ChatRetrievalOut):
    items: list[ChatRetrievalItemOut] = []


class ChatCitationOut(BaseModel):
    assistant_message_id: UUID
    retrieval_id: UUID
    chunk_id: UUID
    document_id: Optional[UUID] = None
    doc_title: Optional[str] = None
    doc_type: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    rank: Optional[int] = None
    score: Optional[float] = None
