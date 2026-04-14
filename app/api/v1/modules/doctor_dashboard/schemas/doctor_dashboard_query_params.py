from __future__ import annotations

from datetime import date
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DoctorDashboardInboxQueryParams(BaseModel):
    q: Optional[str] = Field(default=None, max_length=255)
    company_code: Optional[str] = Field(default=None, max_length=50)
    location_id: Optional[UUID] = Field(default=None)
    building_id: Optional[UUID] = Field(default=None)
    room_id: Optional[UUID] = Field(default=None)
    patient_id: Optional[UUID] = Field(default=None)
    primary_person_id: Optional[UUID] = Field(default=None)

    booking_date: Optional[date] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=25)
    consultation_type: Optional[str] = Field(default=None, max_length=25)
    note_status: Optional[str] = Field(default=None, max_length=25)

    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

    sort_by: Literal[
        "booking_date",
        "start_time",
        "end_time",
        "status",
        "consultation_type",
        "note_status",
        "patient_name",
        "patient_code",
        "location_name",
        "staff_name",
        "service_name",
    ] = Field(default="start_time")

    sort_dir: Literal["asc", "desc"] = Field(default="asc")


class DoctorDashboardInboxSummaryQueryParams(BaseModel):
    company_code: Optional[str] = Field(default=None, max_length=50)
    location_id: Optional[UUID] = Field(default=None)
    building_id: Optional[UUID] = Field(default=None)
    room_id: Optional[UUID] = Field(default=None)
    primary_person_id: Optional[UUID] = Field(default=None)
    booking_date: Optional[date] = Field(default=None)


class DoctorDashboardInboxBookingByIdQueryParams(BaseModel):
    company_code: Optional[str] = Field(default=None, max_length=50)