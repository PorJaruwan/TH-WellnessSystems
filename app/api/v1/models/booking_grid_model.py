# app/api/v1/models/booking_grid_model.py

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Generic, List, Literal, Optional, TypeAlias, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


# ==========================================================
# Base Models (match patients/bookings style)
# ==========================================================
class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class APIBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


# ==========================================================
# Booking Grid Core Models
# ==========================================================
class BookingGridSlot(ORMBaseModel):
    room_id: UUID
    status: str
    booking_id: Optional[UUID] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    service_name: Optional[str] = None

    # ✅ NEW
    patient_id: Optional[UUID] = None
    doctor_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    note: Optional[str] = None

    status_label: Optional[str] = None


class BookingGridTimeRow(ORMBaseModel):
    time: str  # "HH:MM"
    slots: List[BookingGridSlot]


class BookingGridRoom(ORMBaseModel):
    room_id: UUID
    room_name: str


# --------------------------
# format = "grid"
# --------------------------
class BookingGridGridPayload(ORMBaseModel):
    date: date
    time_from: str
    time_to: str
    slot_min: int
    rooms: List[BookingGridRoom]
    timeslots: List[BookingGridTimeRow]
    page: int
    total_pages: int


# --------------------------
# format = "flat"
# --------------------------
class BookingGridFlatItem(ORMBaseModel):
    time: str
    room_id: UUID
    room_name: str
    status: str
    status_label: str
    booking_id: Optional[UUID] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    service_name: Optional[str] = None
    # ✅ NEW
    patient_id: Optional[UUID] = None
    doctor_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    note: Optional[str] = None


class BookingGridFlatPayload(ORMBaseModel):
    date: date
    time_from: str
    time_to: str
    slot_min: int
    rooms: List[BookingGridRoom]
    page: int
    total_pages: int
    total: int
    items: List[BookingGridFlatItem]


# --------------------------
# format = "columns"
# --------------------------
class BookingGridColumn(ORMBaseModel):
    col: int
    room_id: Optional[UUID] = None
    room_name: Optional[str] = None


class BookingGridCell(ORMBaseModel):
    room_id: Optional[UUID] = None
    status: str
    status_label: Optional[str] = None
    booking_id: Optional[UUID] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    service_name: Optional[str] = None
     # ✅ NEW
    patient_id: Optional[UUID] = None
    doctor_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    note: Optional[str] = None


class BookingGridColumnsRow(ORMBaseModel):
    time: str
    # allow dynamic fields: col1..colN
    model_config = ConfigDict(extra="allow")


class BookingGridColumnsPayload(ORMBaseModel):
    date: date
    time_from: str
    time_to: str
    slot_min: int
    page: int
    total_pages: int
    columns: List[BookingGridColumn]
    rows: List[BookingGridColumnsRow]


# ==========================================================
# Type-safe Envelopes (match ResponseHandler)
# ==========================================================
T = TypeVar("T")


class SuccessEnvelope(ORMBaseModel, Generic[T]):
    status: Literal["success"]
    message: str
    data: T


class ErrorEnvelope(ORMBaseModel):
    status: Literal["error"]
    error_code: str
    message: str
    details: Dict[str, Any] = {}


BookingGridAny: TypeAlias = BookingGridGridPayload | BookingGridFlatPayload | BookingGridColumnsPayload
BookingGridEnvelope: TypeAlias = SuccessEnvelope[BookingGridAny] | ErrorEnvelope
