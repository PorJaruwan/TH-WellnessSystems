from __future__ import annotations

"""Envelope bindings for Chat module.

NOTE:
This module keeps envelope shapes aligned with ApiResponse.ok/err used across WellPlus.
Single-item endpoints return data={"item": ...}
List endpoints return ListPayload (via build_list_payload).
"""

from typing import Any, Optional

from pydantic import BaseModel

from app.api.v1.modules.chat.models.dtos import (
    ChatCreateSessionPayload,
    ChatSendMessagePayload,
    ChatSessionHeaderPayload,
    ChatSoftDeleteMessagePayload,
    ChatCitationsPayload,
)


class ItemPayload(BaseModel):
    item: Any


class ChatSessionHeaderEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[ItemPayload] = None


class ChatMessagesEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # ListPayload


class ChatSendMessageEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[ItemPayload] = None


class ChatCreateSessionEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[ItemPayload] = None


class ChatSessionSummaryListEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # ListPayload


class ChatSoftDeleteMessageEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[ItemPayload] = None


class ChatCitationsEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[ItemPayload] = None
