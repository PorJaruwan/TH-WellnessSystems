# app/api/v1/models/staff_response_model.py

from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# =========================================================
# Staff
# =========================================================
class StaffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    staff_name: str
    role: str

    license_number: Optional[str] = None
    specialty: Optional[str] = None

    phone: Optional[str] = None
    email: Optional[str] = None

    gender: Optional[str] = None
    avatar_url: Optional[str] = None

    main_location_id: Optional[UUID] = None
    main_building_id: Optional[UUID] = None
    main_room_id: Optional[UUID] = None

    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Staff Departments
# =========================================================
class StaffDepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    staff_id: UUID
    department_id: UUID

    role_in_dept: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Staff Locations
# =========================================================
class StaffLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    staff_id: UUID
    location_id: UUID

    work_days: Optional[str] = None
    work_time_from: Optional[time] = None
    work_time_to: Optional[time] = None

    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Staff Services
# =========================================================
class StaffServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    staff_id: UUID
    service_id: UUID

    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Staff Template
# =========================================================
class StaffTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    shift_code: str
    shift_name: Optional[str] = None

    start_time: time
    end_time: time
    is_overnight: bool

    description: Optional[str] = None
    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Staff Work Pattern
# =========================================================
class StaffWorkPatternResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    staff_id: UUID
    location_id: UUID
    department_id: UUID
    weekday: int
    shift_template_id: UUID

    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Staff Leave
# =========================================================
class StaffLeaveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    company_code: str
    location_id: UUID
    staff_id: UUID

    leave_type: str
    date_from: date
    date_to: date

    part_of_day: Optional[str] = None
    status: str
    reason: Optional[str] = None

    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None

    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
