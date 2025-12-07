# app/api/v1/bookings/doctor_schedule_model.py
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
#from datetime import datetime


# ==============================
#get_doctor_schedule
# ==============================
# ✅ Request model
class ScheduleRequest(BaseModel):
    """
    Request body for fetching doctor schedule on a specific date
    with optional filters.
    """
    target_date: str = Field(..., example="2025-07-21", description="The date to query schedule (YYYY-MM-DD)")
    doctor_input: Optional[UUID] = Field(None, example="3c9fc805-a241-416c-9614-6ba879a48b6f", description="Filter by doctor's UUID")
    location_input: Optional[UUID] = Field(None, example="3fa85f64-5717-4562-b3fc-2c963f66afa9", description="Filter by location UUID")
    patient_input: Optional[UUID] = Field(None, example="3fa85f64-5717-4562-b3fc-2c963f66afa7", description="Filter by patient UUID")
    service_status_input: Optional[str] = Field(None, example="confirmed", description="Filter by service status (pending, confirmed, completed, cancelled)")
    slot_minutes: Optional[int] = Field(30, example=30, description="Duration of each time slot in minutes")

# ✅ Response item model
class ScheduleItem(BaseModel):
    location_name: Optional[str]
    doctor_name: Optional[str]
    nurse_name: Optional[str]
    slot_start_time: Optional[str]  # Format HH:MM:SS
    slot_end_time: Optional[str]
    patient_name: Optional[str]
    service_name: Optional[str]
    room_name: Optional[str]
    service_status: Optional[str]
    description: Optional[str]
    unavailable_reason: Optional[str]
    doctor_id: Optional[UUID]
    nurse_id: Optional[UUID]
    patient_id: Optional[UUID]
    service_id: Optional[UUID]
    room_id: Optional[UUID]

# ✅ Full response structure
class ScheduleResponse(BaseModel):
    message: str = Field(..., example="Fetched doctor schedule successfully.")
    data: List[ScheduleItem]
