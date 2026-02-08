# app/api/v1/models/_envelopes/base.py

from __future__ import annotations

from typing import Any, Dict, Generic, Literal, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class EnvelopeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SuccessEnvelope(EnvelopeBase, Generic[T]):
    status: Literal["success"] = "success"
    status_code: int = Field(default=200, description="Mirror HTTP status code.")
    message: str
    data: T


class ErrorEnvelope(EnvelopeBase):
    status: Literal["error"] = "error"
    status_code: int = Field(..., description="Mirror HTTP status code.")
    error_code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

