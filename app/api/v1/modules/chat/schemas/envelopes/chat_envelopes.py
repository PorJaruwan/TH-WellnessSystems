# app/api/v1/modules/chat/schemas/envelopes/chat_envelopes.py


from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel
from app.api.v1.modules.chat.schemas.chat_model import (
    ChatSessionHeaderPayload,
    ChatMessageItem,
    ChatSendMessagePayload,
)

class ChatSessionHeaderEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[ChatSessionHeaderPayload] = None


class ChatMessagesEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # {items, limit, before}


class ChatSendMessageEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[ChatSendMessagePayload] = None
