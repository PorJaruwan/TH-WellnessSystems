from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMDTO(BaseModel):
    """DTO base with ORM mode enabled."""

    model_config = ConfigDict(from_attributes=True)


class StaffSearchItemDTO(ORMDTO):
    id: UUID
    staff_name: str
    role: str

    phone: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None
    specialty: Optional[str] = None
    is_active: Optional[bool] = None


class StaffDetailDTO(ORMDTO):
    """Full staff detail (extend as needed)."""

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
    main_department_id: Optional[UUID] = None
    is_active: Optional[bool] = None



# =========================================================
# Staff Departments / Services / Leave DTOs
# =========================================================
from datetime import date, datetime
from typing import Optional


class StaffDepartmentDTO(ORMDTO):
    id: UUID
    staff_id: UUID
    department_id: UUID
    role_in_dept: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StaffServiceDTO(ORMDTO):
    id: UUID
    staff_id: UUID
    service_id: UUID
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StaffLeaveDTO(ORMDTO):
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
