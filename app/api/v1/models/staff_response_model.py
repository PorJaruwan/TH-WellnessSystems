# app/api/v1/models/staff_response_model.py

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, TypeAlias
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.api.v1.models.bookings_model import SuccessEnvelope, ErrorEnvelope


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# Staff
# =========================================================
class StaffResponse(ORMBaseModel):
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


class StaffSearchData(ORMBaseModel):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    staff: List[StaffResponse]


class StaffByIdData(ORMBaseModel):
    staff: StaffResponse


class StaffCreateData(ORMBaseModel):
    staff: StaffResponse


class StaffUpdateData(ORMBaseModel):
    staff: StaffResponse


class StaffDeleteData(ORMBaseModel):
    staff_id: str


StaffSearchEnvelope: TypeAlias = SuccessEnvelope[StaffSearchData] | ErrorEnvelope
StaffByIdEnvelope: TypeAlias = SuccessEnvelope[StaffByIdData] | ErrorEnvelope
StaffCreateEnvelope: TypeAlias = SuccessEnvelope[StaffCreateData] | ErrorEnvelope
StaffUpdateEnvelope: TypeAlias = SuccessEnvelope[StaffUpdateData] | ErrorEnvelope
StaffDeleteEnvelope: TypeAlias = SuccessEnvelope[StaffDeleteData] | ErrorEnvelope


# =========================================================
# Staff Departments
# =========================================================
class StaffDepartmentResponse(ORMBaseModel):
    id: UUID
    staff_id: UUID
    department_id: UUID

    role_in_dept: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StaffDepartmentSearchData(ORMBaseModel):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    staff_departments: List[StaffDepartmentResponse]


class StaffDepartmentByIdData(ORMBaseModel):
    staff_departments: StaffDepartmentResponse


class StaffDepartmentCreateData(ORMBaseModel):
    staff_departments: StaffDepartmentResponse


class StaffDepartmentUpdateData(ORMBaseModel):
    staff_departments: StaffDepartmentResponse


class StaffDepartmentDeleteData(ORMBaseModel):
    staff_department_id: str


StaffDepartmentSearchEnvelope: TypeAlias = SuccessEnvelope[StaffDepartmentSearchData] | ErrorEnvelope
StaffDepartmentByIdEnvelope: TypeAlias = SuccessEnvelope[StaffDepartmentByIdData] | ErrorEnvelope
StaffDepartmentCreateEnvelope: TypeAlias = SuccessEnvelope[StaffDepartmentCreateData] | ErrorEnvelope
StaffDepartmentUpdateEnvelope: TypeAlias = SuccessEnvelope[StaffDepartmentUpdateData] | ErrorEnvelope
StaffDepartmentDeleteEnvelope: TypeAlias = SuccessEnvelope[StaffDepartmentDeleteData] | ErrorEnvelope


# =========================================================
# Staff Locations
# =========================================================
class StaffLocationResponse(ORMBaseModel):
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


class StaffLocationSearchData(ORMBaseModel):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    staff_locations: List[StaffLocationResponse]


class StaffLocationByIdData(ORMBaseModel):
    staff_locations: StaffLocationResponse


class StaffLocationCreateData(ORMBaseModel):
    staff_locations: StaffLocationResponse


class StaffLocationUpdateData(ORMBaseModel):
    staff_locations: StaffLocationResponse


class StaffLocationDeleteData(ORMBaseModel):
    staff_location_id: str


StaffLocationSearchEnvelope: TypeAlias = SuccessEnvelope[StaffLocationSearchData] | ErrorEnvelope
StaffLocationByIdEnvelope: TypeAlias = SuccessEnvelope[StaffLocationByIdData] | ErrorEnvelope
StaffLocationCreateEnvelope: TypeAlias = SuccessEnvelope[StaffLocationCreateData] | ErrorEnvelope
StaffLocationUpdateEnvelope: TypeAlias = SuccessEnvelope[StaffLocationUpdateData] | ErrorEnvelope
StaffLocationDeleteEnvelope: TypeAlias = SuccessEnvelope[StaffLocationDeleteData] | ErrorEnvelope


# =========================================================
# Staff Services
# =========================================================
class StaffServiceResponse(ORMBaseModel):
    id: UUID
    staff_id: UUID
    service_id: UUID

    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StaffServiceSearchData(ORMBaseModel):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    staff_services: List[StaffServiceResponse]


class StaffServiceByIdData(ORMBaseModel):
    staff_services: StaffServiceResponse


class StaffServiceCreateData(ORMBaseModel):
    staff_services: StaffServiceResponse


class StaffServiceUpdateData(ORMBaseModel):
    staff_services: StaffServiceResponse


class StaffServiceDeleteData(ORMBaseModel):
    staff_service_id: str


StaffServiceSearchEnvelope: TypeAlias = SuccessEnvelope[StaffServiceSearchData] | ErrorEnvelope
StaffServiceByIdEnvelope: TypeAlias = SuccessEnvelope[StaffServiceByIdData] | ErrorEnvelope
StaffServiceCreateEnvelope: TypeAlias = SuccessEnvelope[StaffServiceCreateData] | ErrorEnvelope
StaffServiceUpdateEnvelope: TypeAlias = SuccessEnvelope[StaffServiceUpdateData] | ErrorEnvelope
StaffServiceDeleteEnvelope: TypeAlias = SuccessEnvelope[StaffServiceDeleteData] | ErrorEnvelope


# =========================================================
# Staff Template
# =========================================================
class StaffTemplateResponse(ORMBaseModel):
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


class StaffTemplateSearchData(ORMBaseModel):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    staff_template: List[StaffTemplateResponse]


class StaffTemplateByIdData(ORMBaseModel):
    staff_template: StaffTemplateResponse


class StaffTemplateCreateData(ORMBaseModel):
    staff_template: StaffTemplateResponse


class StaffTemplateUpdateData(ORMBaseModel):
    staff_template: StaffTemplateResponse


class StaffTemplateDeleteData(ORMBaseModel):
    staff_template_id: str


StaffTemplateSearchEnvelope: TypeAlias = SuccessEnvelope[StaffTemplateSearchData] | ErrorEnvelope
StaffTemplateByIdEnvelope: TypeAlias = SuccessEnvelope[StaffTemplateByIdData] | ErrorEnvelope
StaffTemplateCreateEnvelope: TypeAlias = SuccessEnvelope[StaffTemplateCreateData] | ErrorEnvelope
StaffTemplateUpdateEnvelope: TypeAlias = SuccessEnvelope[StaffTemplateUpdateData] | ErrorEnvelope
StaffTemplateDeleteEnvelope: TypeAlias = SuccessEnvelope[StaffTemplateDeleteData] | ErrorEnvelope


# =========================================================
# Staff Work Pattern  ✅ (เพิ่ม)
# =========================================================
class StaffWorkPatternResponse(ORMBaseModel):
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


class StaffWorkPatternSearchData(ORMBaseModel):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    staff_work_pattern: List[StaffWorkPatternResponse]


class StaffWorkPatternByIdData(ORMBaseModel):
    staff_work_pattern: StaffWorkPatternResponse


class StaffWorkPatternCreateData(ORMBaseModel):
    staff_work_pattern: StaffWorkPatternResponse


class StaffWorkPatternUpdateData(ORMBaseModel):
    staff_work_pattern: StaffWorkPatternResponse


class StaffWorkPatternDeleteData(ORMBaseModel):
    pattern_id: str


StaffWorkPatternSearchEnvelope: TypeAlias = SuccessEnvelope[StaffWorkPatternSearchData] | ErrorEnvelope
StaffWorkPatternByIdEnvelope: TypeAlias = SuccessEnvelope[StaffWorkPatternByIdData] | ErrorEnvelope
StaffWorkPatternCreateEnvelope: TypeAlias = SuccessEnvelope[StaffWorkPatternCreateData] | ErrorEnvelope
StaffWorkPatternUpdateEnvelope: TypeAlias = SuccessEnvelope[StaffWorkPatternUpdateData] | ErrorEnvelope
StaffWorkPatternDeleteEnvelope: TypeAlias = SuccessEnvelope[StaffWorkPatternDeleteData] | ErrorEnvelope


# =========================================================
# Staff Leave ✅ (เพิ่ม)
# =========================================================
class StaffLeaveResponse(ORMBaseModel):
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


class StaffLeaveSearchData(ORMBaseModel):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    staff_leave: List[StaffLeaveResponse]


class StaffLeaveByIdData(ORMBaseModel):
    staff_leave: StaffLeaveResponse


class StaffLeaveCreateData(ORMBaseModel):
    staff_leave: StaffLeaveResponse


class StaffLeaveUpdateData(ORMBaseModel):
    staff_leave: StaffLeaveResponse


class StaffLeaveDeleteData(ORMBaseModel):
    leave_id: str


StaffLeaveSearchEnvelope: TypeAlias = SuccessEnvelope[StaffLeaveSearchData] | ErrorEnvelope
StaffLeaveByIdEnvelope: TypeAlias = SuccessEnvelope[StaffLeaveByIdData] | ErrorEnvelope
StaffLeaveCreateEnvelope: TypeAlias = SuccessEnvelope[StaffLeaveCreateData] | ErrorEnvelope
StaffLeaveUpdateEnvelope: TypeAlias = SuccessEnvelope[StaffLeaveUpdateData] | ErrorEnvelope
StaffLeaveDeleteEnvelope: TypeAlias = SuccessEnvelope[StaffLeaveDeleteData] | ErrorEnvelope

