# app/api/v1/models/bookings_model.py
from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
from typing import Any, Dict, Generic, List, Literal, Optional, TypeAlias, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =========================================================
# Base Models (same style as patients_model.py)
# =========================================================
class ORMBaseModel(BaseModel):
    """Base for response/read models created from ORM objects."""
    model_config = ConfigDict(from_attributes=True)


class APIBaseModel(BaseModel):
    """
    Base for request payload models (Level 3):
    - forbid extra fields automatically
    - strip whitespace on strings
    - convert empty strings "" -> None (before validation)
    """
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @field_validator("*", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


# ==========================================================
# Enums (match DB constraints)
# ==========================================================
class BookingStatusEnum(str, Enum):
    available = "available"
    draft = "draft"
    booked = "booked"
    confirmed = "confirmed"
    checked_in = "checked_in"
    in_service = "in_service"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"
    rescheduled = "rescheduled"


class SourceOfAdEnum(str, Enum):
    online = "online"
    walk_in = "walk_in"
    call_center = "call_center"
    line = "line"


# ==========================================================
# Bookings (Request: Create / Update)
# ==========================================================
class BookingCreate(APIBaseModel):
    """
    POST /api/v1/bookings
    """
    # resource_track_id: UUID
    company_code: str = Field(..., max_length=50)

    location_id: UUID
    building_id: UUID
    room_id: UUID

    patient_id: UUID
    primary_person_id: UUID
    service_id: UUID

    booking_date: date
    start_time: time
    end_time: time

    status: BookingStatusEnum = BookingStatusEnum.booked
    source_of_ad: Optional[SourceOfAdEnum] = None
    note: Optional[str] = None
    cancel_reason: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, end_t: time, info):
        start_t = info.data.get("start_time")
        if isinstance(start_t, time) and end_t <= start_t:
            raise ValueError("end_time must be after start_time")
        return end_t


class BookingUpdate(APIBaseModel):
    """
    PATCH /api/v1/bookings/{booking_id}
    (Partial update: set only provided fields)
    """
    # resource_track_id: Optional[UUID] = None
    company_code: Optional[str] = Field(None, max_length=50)

    location_id: Optional[UUID] = None
    building_id: Optional[UUID] = None
    room_id: Optional[UUID] = None

    patient_id: Optional[UUID] = None
    primary_person_id: Optional[UUID] = None
    service_id: Optional[UUID] = None

    booking_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    status: Optional[BookingStatusEnum] = None
    source_of_ad: Optional[SourceOfAdEnum] = None
    note: Optional[str] = None
    cancel_reason: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start_when_both_present(cls, end_t: Optional[time], info):
        start_t = info.data.get("start_time")
        if isinstance(start_t, time) and isinstance(end_t, time) and end_t <= start_t:
            raise ValueError("end_time must be after start_time")
        return end_t


class BookingUpdateNote(APIBaseModel):
    """
    PATCH /api/v1/bookings/{booking_id}/note
    """
    note: str = Field(..., min_length=1, description="Update booking note")


# ==========================================================
# Bookings (Read)
# ==========================================================
class BookingRead(ORMBaseModel):
    """
    Standard booking record (read)
    """
    id: UUID

    resource_track_id: UUID
    company_code: str

    location_id: UUID
    building_id: UUID
    room_id: UUID

    patient_id: UUID
    primary_person_id: UUID
    service_id: UUID

    booking_date: date
    start_time: time
    end_time: time

    status: BookingStatusEnum
    source_of_ad: Optional[SourceOfAdEnum] = None
    note: Optional[str] = None
    cancel_reason: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Booking Grid View (used by booking_grid_view)
# ==========================================================
class BookingListItem(ORMBaseModel):
    """
    Item for booking grid list/search
    """
    id: UUID
    booking_date: date
    start_time: str
    end_time: str
    status: str

    room_name: str = ""
    patient_name: str = ""
    doctor_name: str = ""
    service_name: str = ""


class BookingDetail(ORMBaseModel):
    """
    Detail response from booking_grid_view
    """
    id: UUID

    company_code: str
    location_id: UUID
    building_id: UUID

    booking_date: date
    start_time: str
    end_time: str
    status: str

    room_id: UUID
    room_name: Optional[str] = None

    patient_id: UUID
    patient_name: Optional[str] = None
    patient_telephone: Optional[str] = None

    doctor_id: UUID
    doctor_name: Optional[str] = None

    service_id: UUID
    service_name: Optional[str] = None

    source_of_ad: Optional[str] = None
    note: Optional[str] = None


# ==========================================================
# Status Action & History
# ==========================================================
class BookingActionEnum(str, Enum):
    """
    Action commands for POST /api/v1/bookings/{booking_id}/status

    - confirm       : Confirm booking -> status=confirmed
    - checkin       : Patient checked-in -> status=checked_in
    - start_service : Start service -> status=in_service
    - complete      : Complete service -> status=completed
    - cancel        : Cancel booking -> status=cancelled (requires cancel_reason)
    - no_show       : Mark no-show -> status=no_show
    - reschedule    : Reschedule -> status=rescheduled
    """
    confirm = "confirm"
    checkin = "checkin"
    start_service = "start_service"
    complete = "complete"
    cancel = "cancel"
    no_show = "no_show"
    reschedule = "reschedule"


class BookingStatusActionBody(APIBaseModel):
    """
    POST /api/v1/bookings/{booking_id}/status
    """
    user_id: UUID
    action: BookingActionEnum = Field(
        ...,
        description=(
            "Booking action command.\n"
            "- confirm: Confirm booking -> confirmed\n"
            "- checkin: Check-in -> checked_in\n"
            "- start_service: Start service -> in_service\n"
            "- complete: Complete -> completed\n"
            "- cancel: Cancel -> cancelled (requires cancel_reason)\n"
            "- no_show: No-show -> no_show\n"
            "- reschedule: Reschedule -> rescheduled"
        ),
    )
    note: Optional[str] = Field(None, description="Optional note for this action")
    cancel_reason: Optional[str] = Field(
        None,
        description="Required only when action='cancel'. Not allowed for other actions.",
    )
    force: bool = Field(False, description="Force apply even if old_status == new_status")

    @field_validator("note", "cancel_reason", mode="before")
    @classmethod
    def _strip_empty_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            vv = v.strip()
            return vv if vv else None
        return v

    @field_validator("cancel_reason")
    @classmethod
    def _validate_cancel_reason_rules(cls, cancel_reason: Optional[str], info):
        """
        Strict rules:
        - action=cancel  -> cancel_reason required
        - other actions  -> cancel_reason must be None
        """
        action = info.data.get("action")
        if action is None:
            return cancel_reason

        if action == BookingActionEnum.cancel:
            if not cancel_reason:
                raise ValueError("cancel_reason is required when action='cancel'")
            return cancel_reason

        if cancel_reason:
            raise ValueError("cancel_reason is only allowed when action='cancel'")
        return None



class BookingHistoryItem(ORMBaseModel):
    id: UUID
    old_status: Optional[str] = None
    new_status: str
    changed_at: str  # ISO string (service convert)
    changed_by: Optional[str] = None
    note: Optional[str] = None


class BookingHistoryResponse(ORMBaseModel):
    booking_id: UUID
    items: List[BookingHistoryItem]


# ==========================================================
# Minimal responses (search/create/update) returned by service
# ==========================================================
class BookingSearchResponse(ORMBaseModel):
    """
    Service-level search response (keep for backward compatibility with service imports)
    """
    limit: int
    offset: int
    total: int
    items: List[BookingListItem]


class BookingCreateResponse(ORMBaseModel):
    id: UUID
    status: str


class BookingUpdateResponse(ORMBaseModel):
    id: UUID
    status: Optional[str] = None
    updated_at: Optional[datetime] = None  # ✅ เปลี่ยนเป็น datetime


# ==========================================================
# Envelope Data Shapes (data=...) for ResponseHandler.success
# ==========================================================
class BookingSearchData(ORMBaseModel):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    bookings: List[BookingListItem]


class BookingByIdData(ORMBaseModel):
    booking: BookingDetail


class BookingCreateData(ORMBaseModel):
    booking: BookingCreateResponse


class BookingUpdateData(ORMBaseModel):
    booking: BookingUpdateResponse


class BookingUpdateNoteData(ORMBaseModel):
    booking_id: str


class BookingStatusActionResult(ORMBaseModel):
    booking_id: UUID
    old_status: Optional[str] = None
    status: str
    updated_at: Optional[datetime] = None  # ✅ เปลี่ยนเป็น datetime

class BookingStatusActionData(ORMBaseModel):
    result: BookingStatusActionResult


class BookingHistoryData(ORMBaseModel):
    booking_id: str
    items: List[BookingHistoryItem]


class BookingDeleteData(ORMBaseModel):
    booking_id: str


# ==========================================================
# Type-safe Envelopes (MATCH ResponseHandler.py)
# success: {status, message, data}
# error:   {status, error_code, message, details}
# ==========================================================
T = TypeVar("T")


class SuccessEnvelope(ORMBaseModel, Generic[T]):
    status: Literal["success"]
    status_code: int = Field(default=200, description="Mirror HTTP status code.")
    message: str
    data: T


class ErrorEnvelope(ORMBaseModel):
    status: Literal["error"]
    status_code: int = Field(..., description="Mirror HTTP status code.")
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional error details (defaults to {})."
    )



# ---- per-endpoint envelope aliases ----
BookingSearchEnvelope: TypeAlias = SuccessEnvelope[BookingSearchData] | ErrorEnvelope
BookingByIdEnvelope: TypeAlias = SuccessEnvelope[BookingByIdData] | ErrorEnvelope
BookingCreateEnvelope: TypeAlias = SuccessEnvelope[BookingCreateData] | ErrorEnvelope
BookingUpdateEnvelope: TypeAlias = SuccessEnvelope[BookingUpdateData] | ErrorEnvelope
BookingUpdateNoteEnvelope: TypeAlias = SuccessEnvelope[BookingUpdateNoteData] | ErrorEnvelope
BookingStatusActionEnvelope: TypeAlias = SuccessEnvelope[BookingStatusActionData] | ErrorEnvelope
BookingHistoryEnvelope: TypeAlias = SuccessEnvelope[BookingHistoryData] | ErrorEnvelope
BookingDeleteEnvelope: TypeAlias = SuccessEnvelope[BookingDeleteData] | ErrorEnvelope
