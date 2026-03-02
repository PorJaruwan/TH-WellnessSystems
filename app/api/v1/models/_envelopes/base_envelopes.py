# ==========================================================
# Type-safe Envelopes (MATCH ResponseHandler.py)
# success: {status, status_code, message, data, meta}
# error:   {status, status_code, error_code, message, details, errors, meta}
#
# ✅ Production-ready improvements:
# - SuccessEnvelope.data is Optional (supports DELETE/PATCH no-content)
# - meta supports multi-tenant + observability (company_code, api_version, processing_ms)
# - Standard ListPayload[T] with filters/sort/paging/items
# - Paging includes returned/has_more/next_offset (better for UI + infinite scroll)
# - Remove duplicate EnvelopeBase definition (no overwrite/alias confusion)
# ==========================================================
# app/api/v1/models/_envelopes/base_envelopes.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ----------------------------------------------------------
# Base model for ORM compatibility (Pydantic v2)
# ----------------------------------------------------------
class ORMBaseModel(BaseModel):
    """Base Pydantic model that supports SQLAlchemy ORM objects (Pydantic v2)."""
    model_config = ConfigDict(from_attributes=True)


# Backward-compat alias (legacy imports)
EnvelopeBase = ORMBaseModel


# ----------------------------------------------------------
# Meta (Operational Metadata) — safe to expose
# ----------------------------------------------------------
class EnvelopeMeta(ORMBaseModel):
    """
    Operational metadata for observability & debugging.
    Keep it non-sensitive and stable.

    Recommended usage:
    - request_id: trace a single request across logs/services
    - company_code: multi-tenant context (WP/TSAG/clinic)
    - api_version: contract version ("v1")
    - processing_ms: performance monitoring
    """

    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    path: Optional[str] = None

    company_code: Optional[str] = None
    api_version: Optional[str] = "v1"
    processing_ms: Optional[int] = None

    # Use UTC timestamp (timezone-aware)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when response is generated",
    )


# ----------------------------------------------------------
# Success Envelope
# ----------------------------------------------------------
class SuccessEnvelope(ORMBaseModel, Generic[T]):
    """Standard success envelope used by all endpoints."""

    status: Literal["success"] = "success"
    status_code: int = Field(default=200, description="Mirror HTTP status code.")
    message: str = "OK"

    # ✅ Optional data for endpoints that return no body content
    data: Optional[T] = None

    meta: Optional[EnvelopeMeta] = None


# ----------------------------------------------------------
# Error Envelope
# ----------------------------------------------------------
class ErrorDetail(ORMBaseModel):
    """
    Structured error detail for validation/field errors.
    Keep small and consistent for frontend mapping.
    """

    field: Optional[str] = None
    issue: Optional[str] = None
    hint: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class ErrorEnvelope(ORMBaseModel):
    """
    Standard error envelope used by all endpoints.

    Notes:
    - error_code: internal stable code (e.g. SYS_001, AUTH_001, BOOK_404)
    - details: flexible technical info (not always shown to end-users)
    - errors: structured field-level errors for UI (optional)
    """

    status: Literal["error"] = "error"
    status_code: int = Field(..., ge=400, le=599, description="Mirror HTTP status code.")
    error_code: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=500)

    details: Dict[str, Any] = Field(default_factory=dict)
    errors: Optional[list[ErrorDetail]] = None

    meta: Optional[EnvelopeMeta] = None


# ----------------------------------------------------------
# Standard List Payload (filters/sort/paging/items)
# ----------------------------------------------------------
class Paging(ORMBaseModel):
    """
    Offset-based paging (fits Supabase/Postgres well).
    """

    total: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)

    # ✅ NEW (optional)
    returned: Optional[int] = Field(default=None, ge=0)
    has_more: Optional[bool] = None
    next_offset: Optional[int] = Field(default=None, ge=0)

    # ✅ cursor pagination (optional)
    cursor: Optional[str] = None
    next_cursor: Optional[str] = None

    # ✅ extra fields for better UX
    returned: Optional[int] = Field(default=None, ge=0, description="Returned items count")
    has_more: Optional[bool] = Field(default=None, description="True if more items exist")
    next_offset: Optional[int] = Field(default=None, ge=0, description="Offset for next page")


class Sort(ORMBaseModel):
    by: str = Field(..., min_length=1)
    order: Literal["asc", "desc"] = "desc"


class ListPayload(ORMBaseModel, Generic[T]):
    """
    Standard shape for list endpoints.

    data = {
      "filters": {...},
      "sort": {...},
      "paging": {...},
      "items": [...]
    }
    """

    filters: Dict[str, Any] = Field(default_factory=dict)
    sort: Optional[Sort] = None
    paging: Optional[Paging] = None
    # ✅ NEW (optional)
    fields: Optional[list[str]] = None      # e.g. ["code","name"]
    includes: Optional[list[str]] = None    # e.g. ["children","relations"]
    aggregations: Optional[Dict[str, Any]] = None  # e.g. {"active": 10, "inactive": 2}

    items: list[T] = Field(default_factory=list)
    
# ----------------------------------------------------------
# (Optional) Page-based pagination (if you still need it)
# Keep for compatibility, but prefer ListPayload + Paging for offset style.
# ----------------------------------------------------------
class PageInfo(ORMBaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=200)
    total: int = Field(0, ge=0)


class PaginatedPayload(ORMBaseModel, Generic[T]):
    items: list[T] = Field(default_factory=list)
    page_info: PageInfo