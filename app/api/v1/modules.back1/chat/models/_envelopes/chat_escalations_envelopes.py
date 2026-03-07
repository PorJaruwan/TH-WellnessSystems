from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ChatEscalationsEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # ListPayload


class ChatEscalationEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[dict[str, Any]] = None  # {item: ...}
