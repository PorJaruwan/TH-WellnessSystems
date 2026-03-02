# app/api/v1/models/base.py
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Base Models
# ==========================================================
class APIBaseModel(BaseModel):
    """
    Base Pydantic model for API layer
    - ORM-friendly (from_attributes=True)
    - Forbid extra fields by default
    """
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        populate_by_name=True,
    )


# ==========================================================
# Envelope Models
# ==========================================================
class BaseEnvelope(APIBaseModel):
    success: bool
    code: str
    message: str


class SuccessEnvelope(BaseEnvelope):
    """
    Standard success response envelope
    """
    success: bool = True
    data: Optional[Any] = None


class ErrorEnvelope(BaseEnvelope):
    """
    Standard error response envelope
    """
    success: bool = False
    details: Optional[Dict[str, Any]] = None
