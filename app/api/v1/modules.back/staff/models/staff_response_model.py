# app\api\v1\modules\staff\models\staff_response_model.py

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, TypeAlias
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ErrorEnvelope, ListPayload

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


StaffSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[StaffResponse]] | ErrorEnvelope
StaffByIdEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffCreateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffUpdateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffDeleteEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
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


StaffDepartmentSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[StaffDepartmentResponse]] | ErrorEnvelope
StaffDepartmentByIdEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffDepartmentCreateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffDepartmentUpdateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffDepartmentDeleteEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
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


StaffLocationSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[StaffLocationResponse]] | ErrorEnvelope
StaffLocationByIdEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffLocationCreateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffLocationUpdateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffLocationDeleteEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
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


StaffServiceSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[StaffServiceResponse]] | ErrorEnvelope
StaffServiceByIdEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffServiceCreateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffServiceUpdateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffServiceDeleteEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
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


StaffTemplateSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[StaffTemplateResponse]] | ErrorEnvelope
StaffTemplateByIdEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffTemplateCreateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffTemplateUpdateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffTemplateDeleteEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
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


StaffWorkPatternSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[StaffWorkPatternResponse]] | ErrorEnvelope
StaffWorkPatternByIdEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffWorkPatternCreateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffWorkPatternUpdateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffWorkPatternDeleteEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
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


StaffLeaveSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[StaffLeaveResponse]] | ErrorEnvelope
StaffLeaveByIdEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffLeaveCreateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffLeaveUpdateEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope
StaffLeaveDeleteEnvelope: TypeAlias = SuccessEnvelope[dict] | ErrorEnvelope