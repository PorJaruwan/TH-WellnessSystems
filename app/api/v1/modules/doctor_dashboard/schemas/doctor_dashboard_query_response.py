from __future__ import annotations

from datetime import date, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DoctorDashboardInboxItemResponse(BaseModel):
    booking_id: UUID
    company_code: str

    location_id: UUID
    location_name: str
    location_code: Optional[str] = None

    building_id: UUID
    building_name: str
    building_code: Optional[str] = None

    room_id: UUID
    room_name: str
    room_code: Optional[str] = None

    patient_id: UUID
    full_name_lo: str
    full_name_en: Optional[str] = None
    patient_code: str

    service_id: UUID
    service_name: str
    service_code: Optional[str] = None

    primary_person_id: UUID
    staff_name: str
    role: str

    booking_date: date
    note: Optional[str] = None
    start_time: time
    end_time: time
    status: str
    consultation_type: Optional[str] = None
    note_status: Optional[str] = None


class DoctorDashboardInboxFiltersResponse(BaseModel):
    q: Optional[str] = None
    company_code: Optional[str] = None
    location_id: Optional[UUID] = None
    building_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    patient_id: Optional[UUID] = None
    primary_person_id: Optional[UUID] = None
    booking_date: Optional[date] = None
    status: Optional[str] = None
    consultation_type: Optional[str] = None
    note_status: Optional[str] = None


class DoctorDashboardInboxSortResponse(BaseModel):
    by: str = "start_time"
    order: str = "asc"


class DoctorDashboardInboxPagingResponse(BaseModel):
    total: int = 0
    limit: int = 20
    offset: int = 0


class DoctorDashboardInboxListResponse(BaseModel):
    filters: DoctorDashboardInboxFiltersResponse
    sort: DoctorDashboardInboxSortResponse
    paging: DoctorDashboardInboxPagingResponse
    items: List[DoctorDashboardInboxItemResponse] = Field(default_factory=list)


class DoctorDashboardInboxSummaryResponse(BaseModel):
    total_all: int = 0
    total_draft_note: int = 0
    total_completed_note: int = 0
    total_signed_note: int = 0
    total_online: int = 0
    total_onsite: int = 0

    total_booked: int = 0
    total_confirmed: int = 0
    total_checked_in: int = 0
    total_in_service: int = 0
    total_completed: int = 0
    total_cancelled: int = 0
    total_no_show: int = 0
    total_rescheduled: int = 0


class DoctorDashboardInboxBookingDetailResponse(BaseModel):
    booking_id: UUID
    company_code: str

    location_id: UUID
    location_name: str
    location_code: Optional[str] = None

    building_id: UUID
    building_name: str
    building_code: Optional[str] = None

    room_id: UUID
    room_name: str
    room_code: Optional[str] = None

    patient_id: UUID
    full_name_lo: str
    full_name_en: Optional[str] = None
    patient_code: str

    service_id: UUID
    service_name: str
    service_code: Optional[str] = None

    primary_person_id: UUID
    staff_name: str
    role: str

    booking_date: date
    note: Optional[str] = None
    start_time: time
    end_time: time
    status: str
    consultation_type: Optional[str] = None
    note_status: Optional[str] = None