from datetime import date, time
from typing import Optional

from pydantic import BaseModel


class DoctorDashboardAcceptBookingRequest(BaseModel):
    updated_by: Optional[str] = None
    note: Optional[str] = None


class DoctorDashboardRejectBookingRequest(BaseModel):
    reason: str
    updated_by: Optional[str] = None


class DoctorDashboardStartConsultationRequest(BaseModel):
    updated_by: Optional[str] = None


class DoctorDashboardRescheduleBookingRequest(BaseModel):
    booking_date: date
    start_time: time
    end_time: time
    room_id: Optional[str] = None
    note: Optional[str] = None
    updated_by: Optional[str] = None


class DoctorDashboardUpdateNoteStatusRequest(BaseModel):
    note_status: str
    updated_by: Optional[str] = None