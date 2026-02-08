# app/api/v1/models/staff_model.py

from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# =========================================================
# Staff
# =========================================================
class StaffCreateModel(BaseModel):
    staff_name: str
    role: str = Field(..., description="doctor|therapist|nurse|staff")

    license_number: Optional[str] = None
    specialty: Optional[str] = None

    phone: Optional[str] = Field(None, description="unique: phone")
    email: Optional[str] = Field(None, description="unique: email")

    gender: Optional[str] = None
    avatar_url: Optional[str] = None

    main_location_id: Optional[UUID] = Field(None, description="FK: locations.id")
    main_building_id: Optional[UUID] = Field(None, description="FK: buildings.id")
    main_room_id: Optional[UUID] = Field(None, description="FK: rooms.id")

    is_active: Optional[bool] = Field(True, description="default true")


class StaffUpdateModel(BaseModel):
    staff_name: Optional[str] = None
    role: Optional[str] = Field(None, description="doctor|therapist|nurse|staff")

    license_number: Optional[str] = None
    specialty: Optional[str] = None

    phone: Optional[str] = Field(None, description="unique: phone")
    email: Optional[str] = Field(None, description="unique: email")

    gender: Optional[str] = None
    avatar_url: Optional[str] = None

    main_location_id: Optional[UUID] = Field(None, description="FK: locations.id")
    main_building_id: Optional[UUID] = Field(None, description="FK: buildings.id")
    main_room_id: Optional[UUID] = Field(None, description="FK: rooms.id")

    is_active: Optional[bool] = None


# =========================================================
# Staff Services
# =========================================================
class StaffServicesCreateModel(BaseModel):
    staff_id: UUID
    service_id: UUID
    duration_minutes: int = Field(30, ge=1, le=1440)
    is_active: Optional[bool] = True


class StaffServicesUpdateModel(BaseModel):
    staff_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    is_active: Optional[bool] = None


# =========================================================
# Staff Locations
# =========================================================
class StaffLocationsCreateModel(BaseModel):
    staff_id: UUID
    location_id: UUID

    work_days: Optional[str] = Field(None, description="e.g. '1,2,3,4,5'")
    work_time_from: Optional[time] = None
    work_time_to: Optional[time] = None

    is_primary: Optional[bool] = False
    is_active: Optional[bool] = True


class StaffLocationsUpdateModel(BaseModel):
    staff_id: Optional[UUID] = None
    location_id: Optional[UUID] = None

    work_days: Optional[str] = None
    work_time_from: Optional[time] = None
    work_time_to: Optional[time] = None

    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


# =========================================================
# Staff Departments
# =========================================================
class StaffDepartmentsCreateModel(BaseModel):
    staff_id: UUID
    department_id: UUID
    role_in_dept: Optional[str] = None
    is_primary: Optional[bool] = False
    is_active: Optional[bool] = True


class StaffDepartmentsUpdateModel(BaseModel):
    staff_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    role_in_dept: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


# =========================================================
# Staff Template
# =========================================================
class StaffTemplateCreateModel(BaseModel):
    shift_code: str = Field(..., max_length=10)
    shift_name: Optional[str] = None

    start_time: time
    end_time: time
    is_overnight: bool = False

    description: Optional[str] = None
    is_active: Optional[bool] = True


class StaffTemplateUpdateModel(BaseModel):
    shift_code: Optional[str] = Field(None, max_length=10)
    shift_name: Optional[str] = None

    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_overnight: Optional[bool] = None

    description: Optional[str] = None
    is_active: Optional[bool] = None


# =========================================================
# Staff Work Pattern
# =========================================================
class StaffWorkPatternCreateModel(BaseModel):
    staff_id: UUID
    location_id: UUID
    department_id: UUID
    weekday: int = Field(..., ge=0, le=6)

    shift_template_id: UUID
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

    is_active: Optional[bool] = True


class StaffWorkPatternUpdateModel(BaseModel):
    staff_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    weekday: Optional[int] = Field(None, ge=0, le=6)

    shift_template_id: Optional[UUID] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

    is_active: Optional[bool] = None


# =========================================================
# Staff Leave
# =========================================================
class StaffLeaveCreateModel(BaseModel):
    company_code: str
    location_id: UUID
    staff_id: UUID

    leave_type: str = Field(..., description="sick|vacation|personal|other")
    date_from: date
    date_to: date

    part_of_day: Optional[str] = Field(None, description="full|morning|afternoon")
    status: str = Field("draft", description="draft|pending|approved|rejected")

    reason: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None

    is_active: Optional[bool] = True


class StaffLeaveUpdateModel(BaseModel):
    company_code: Optional[str] = None
    location_id: Optional[UUID] = None
    staff_id: Optional[UUID] = None

    leave_type: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    part_of_day: Optional[str] = None
    status: Optional[str] = None

    reason: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None

    is_active: Optional[bool] = None



##2026-01-31
# # app/api/v1/settings/setting_model.py
# from pydantic import BaseModel, Field
# from uuid import UUID
# from datetime import datetime
# from typing import Optional

# # ==============================
# #Staff
# # ==============================
# class StaffCreateModel(BaseModel):
#     id: UUID
#     staff_name: str
#     role: str = Field(None, description="check: doctor, therapist, nurse, staff")
#     license_number: str
#     specialty: str
#     phone: str = Field(None, description="unique: phone")
#     email: str = Field(None, description="unique: email")
#     is_active: bool = Field(None, description="default true")
#     created_at: Optional[datetime] = Field(None, description="Timestamp")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp")
#     gender: str
#     avatar_url: str
#     main_location_id: Optional[str] = Field(None, description="foreign key: location id")
#     main_building_id: Optional[str] = Field(None, description="foreign key: building id")
#     main_room_id: Optional[str] = Field(None, description="foreign key: room id")

# class StaffUpdateModel(BaseModel):
#     staff_name: str
#     role: str = Field(None, description="check: doctor, therapist, nurse, staff")
#     license_number: str
#     specialty: str
#     phone: str = Field(None, description="unique: phone")
#     email: str = Field(None, description="unique: email")
#     is_active: bool = Field(None, description="default true")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp")
#     gender: str
#     avatar_url: str
#     main_location_id: Optional[str] = Field(None, description="foreign key: location id")
#     main_building_id: Optional[str] = Field(None, description="foreign key: building id")
#     main_room_id: Optional[str] = Field(None, description="foreign key: room id")


# # ==============================
# #Staff Services
# # ==============================
# class StaffServicesCreateModel(BaseModel):
#     id: UUID
#     staff_id: str = Field(None, description="foreign key: staff id")
#     service_id: str = Field(None, description="foreign key: service id")
#     duration_minutes: int
#     is_active: bool = Field(None, description="default true")
#     created_at: Optional[datetime] = Field(None, description="Timestamp")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp")

# class StaffServicesUpdateModel(BaseModel):
#     staff_id: str = Field(None, description="foreign key: staff id")
#     service_id: str = Field(None, description="foreign key: service id")
#     duration_minutes: int
#     is_active: bool = Field(None, description="default true")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp")


# # ==============================
# #Staff Locations
# # ==============================
# class StaffLocationsCreateModel(BaseModel):
#     id: UUID
#     staff_id: str = Field(None, description="foreign key: staff id")
#     location_id: str = Field(None, description="foreign key: location id")
#     work_days: str
#     work_time_from: datetime
#     work_time_to: datetime
#     is_primary: bool = Field(None, description="default false")
#     is_active: bool = Field(None, description="default true")
#     created_at: Optional[datetime] = Field(None, description="Timestamp")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp")

# class StaffLocationsUpdateModel(BaseModel):
#     staff_id: str = Field(None, description="foreign key: staff id")
#     location_id: str = Field(None, description="foreign key: location id")
#     work_days: str
#     work_time_from: datetime
#     work_time_to: datetime
#     is_primary: bool = Field(None, description="default false")
#     is_active: bool = Field(None, description="default true")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp")

# # ==============================
# #Staff Departments
# # ==============================
# class StaffDepartmentsCreateModel(BaseModel):
#     id: UUID
#     staff_id: str = Field(None, description="foreign key: staff id")
#     department_id: str = Field(None, description="foreign key: department id")
#     role_in_dept: str
#     is_primary: bool = Field(None, description="default false")
#     is_active: bool = Field(None, description="default true")
#     created_at: Optional[datetime] = Field(None, description="Timestamp")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp")

# class StaffDepartmentsUpdateModel(BaseModel):
#     staff_id: str = Field(None, description="foreign key: staff id")
#     department_id: str = Field(None, description="foreign key: department id")
#     role_in_dept: str
#     is_primary: bool = Field(None, description="default false")
#     is_active: bool = Field(None, description="default true")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp")

# # ==============================
# #Staff Work Pattern
# # ==============================
# class StaffWorkPatternCreateModel(BaseModel):
#     id: UUID
#     staff_id: str = Field(None, description="foreign key: staff id")
#     location_id: str = Field(None, description="foreign key: location id")
#     department_id: str = Field(None, description="foreign key: department id")
#     weekday: int
#     shift_template_id: str
#     valid_from: datetime
#     valid_to: datetime
#     is_active: bool = Field(None, description="default true")

# class StaffWorkPatternUpdateModel(BaseModel):
#     staff_id: str = Field(None, description="foreign key: staff id")
#     location_id: str = Field(None, description="foreign key: location id")
#     department_id: str = Field(None, description="foreign key: department id")
#     weekday: int
#     shift_template_id: str
#     valid_from: datetime
#     valid_to: datetime
#     is_active: bool = Field(None, description="default active is true")

# # ==============================
# #Staff Template
# # ==============================
# class StaffTemplateCreateModel(BaseModel):
#     id: UUID
#     shift_code: str
#     shift_name: str
#     start_time: datetime
#     end_time: datetime
#     is_overnight: bool
#     description: str
#     is_active: bool = Field(None, description="default active is true")

# class StaffTemplateUpdateModel(BaseModel):
#     shift_code: str
#     shift_name: str
#     start_time: datetime
#     end_time: datetime
#     is_overnight: bool
#     description: str
#     is_active: bool = Field(None, description="default active is true")

# # ==============================
# #Staff Leave
# # ==============================
# class StaffLeaveCreateModel(BaseModel):
#     id: UUID
#     company_code: str
#     location_id: str
#     staff_id: str
#     leave_type: str
#     date_from: datetime
#     date_to: datetime
#     part_of_day: str
#     status: str
#     reason: str
#     approved_at: datetime
#     approved_by: str
#     is_active: bool = Field(None, description="default active is true")

# class StaffLeaveUpdateModel(BaseModel):
#     company_code: str
#     location_id: str
#     staff_id: str
#     leave_type: str
#     date_from: datetime
#     date_to: datetime
#     part_of_day: str
#     status: str
#     reason: str
#     approved_at: datetime
#     approved_by: str
#     is_active: bool = Field(None, description="default active is true")


