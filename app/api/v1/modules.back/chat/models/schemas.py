from __future__ import annotations

"""Request schemas (Inbound) for Chat module.

WellPlus API Module Standard:
- schemas.py MUST contain Request models only.
- Response/DTO models MUST be in dtos.py.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatCreateSessionRequest(BaseModel):
    topic_code: Optional[str] = Field(default=None, max_length=100)
    language: str = Field(default="th-TH", max_length=20)
    channel: str = Field(default="flutterflow", max_length=50)
    reuse_open: bool = Field(
        default=True,
        description="If true, reuse existing open session when DB enforces uniqueness",
    )


class ChatSendMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


class ChatEscalationUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_staff_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None
    resolution_note: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRetrievalCreateRequest(BaseModel):
    session_id: UUID
    assistant_message_id: Optional[UUID] = None
    query_text: Optional[str] = None
    query_hash: Optional[str] = None
    top_k: int = Field(default=8, ge=1, le=50)
    filters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRetrievalItemCreateRequest(BaseModel):
    chunk_id: UUID
    document_id: Optional[UUID] = None
    rank: int = Field(ge=1, le=200)
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
