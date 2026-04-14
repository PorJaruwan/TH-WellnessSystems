from datetime import date, time
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel


SortDir = Literal["asc", "desc"]


class DoctorDashboardInboxItem(BaseModel):
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