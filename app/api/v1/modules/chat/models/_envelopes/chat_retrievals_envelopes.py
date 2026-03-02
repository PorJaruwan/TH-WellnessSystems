from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ChatRetrievalEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # {item: ...}


class ChatRetrievalItemsEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # {items: [...]}


class ChatRetrievalDetailEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # {item: ...}


class ChatRetrievalListEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # ListPayload or {items: ...}
