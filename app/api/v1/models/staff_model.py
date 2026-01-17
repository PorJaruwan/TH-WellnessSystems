# app/api/v1/settings/setting_model.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# ==============================
#Staff
# ==============================
class StaffCreateModel(BaseModel):
    id: UUID
    staff_name: str
    role: str = Field(None, description="check: doctor, therapist, nurse, staff")
    license_number: str
    specialty: str
    phone: str = Field(None, description="unique: phone")
    email: str = Field(None, description="unique: email")
    is_active: bool = Field(None, description="default true")
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
    gender: str
    avatar_url: str
    main_location_id: Optional[str] = Field(None, description="foreign key: location id")
    main_building_id: Optional[str] = Field(None, description="foreign key: building id")
    main_room_id: Optional[str] = Field(None, description="foreign key: room id")

class StaffUpdateModel(BaseModel):
    staff_name: str
    role: str = Field(None, description="check: doctor, therapist, nurse, staff")
    license_number: str
    specialty: str
    phone: str = Field(None, description="unique: phone")
    email: str = Field(None, description="unique: email")
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
    gender: str
    avatar_url: str
    main_location_id: Optional[str] = Field(None, description="foreign key: location id")
    main_building_id: Optional[str] = Field(None, description="foreign key: building id")
    main_room_id: Optional[str] = Field(None, description="foreign key: room id")


# ==============================
#Staff Services
# ==============================
class StaffServicesCreateModel(BaseModel):
    id: UUID
    staff_id: str = Field(None, description="foreign key: staff id")
    service_id: str = Field(None, description="foreign key: service id")
    duration_minutes: int
    is_active: bool = Field(None, description="default true")
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

class StaffServicesUpdateModel(BaseModel):
    staff_id: str = Field(None, description="foreign key: staff id")
    service_id: str = Field(None, description="foreign key: service id")
    duration_minutes: int
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")


# ==============================
#Staff Locations
# ==============================
class StaffLocationsCreateModel(BaseModel):
    id: UUID
    staff_id: str = Field(None, description="foreign key: staff id")
    location_id: str = Field(None, description="foreign key: location id")
    work_days: str
    work_time_from: datetime
    work_time_to: datetime
    is_primary: bool = Field(None, description="default false")
    is_active: bool = Field(None, description="default true")
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

class StaffLocationsUpdateModel(BaseModel):
    staff_id: str = Field(None, description="foreign key: staff id")
    location_id: str = Field(None, description="foreign key: location id")
    work_days: str
    work_time_from: datetime
    work_time_to: datetime
    is_primary: bool = Field(None, description="default false")
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

# ==============================
#Staff Departments
# ==============================
class StaffDepartmentsCreateModel(BaseModel):
    id: UUID
    staff_id: str = Field(None, description="foreign key: staff id")
    department_id: str = Field(None, description="foreign key: department id")
    role_in_dept: str
    is_primary: bool = Field(None, description="default false")
    is_active: bool = Field(None, description="default true")
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

class StaffDepartmentsUpdateModel(BaseModel):
    staff_id: str = Field(None, description="foreign key: staff id")
    department_id: str = Field(None, description="foreign key: department id")
    role_in_dept: str
    is_primary: bool = Field(None, description="default false")
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

# ==============================
#Staff Work Pattern
# ==============================
class StaffWorkPatternCreateModel(BaseModel):
    id: UUID
    staff_id: str = Field(None, description="foreign key: staff id")
    location_id: str = Field(None, description="foreign key: location id")
    department_id: str = Field(None, description="foreign key: department id")
    weekday: int
    shift_template_id: str
    valid_from: datetime
    valid_to: datetime
    is_active: bool = Field(None, description="default true")

class StaffWorkPatternUpdateModel(BaseModel):
    staff_id: str = Field(None, description="foreign key: staff id")
    location_id: str = Field(None, description="foreign key: location id")
    department_id: str = Field(None, description="foreign key: department id")
    weekday: int
    shift_template_id: str
    valid_from: datetime
    valid_to: datetime
    is_active: bool = Field(None, description="default active is true")

# ==============================
#Staff Template
# ==============================
class StaffTemplateCreateModel(BaseModel):
    id: UUID
    shift_code: str
    shift_name: str
    start_time: datetime
    end_time: datetime
    is_overnight: bool
    description: str
    is_active: bool = Field(None, description="default active is true")

class StaffTemplateUpdateModel(BaseModel):
    shift_code: str
    shift_name: str
    start_time: datetime
    end_time: datetime
    is_overnight: bool
    description: str
    is_active: bool = Field(None, description="default active is true")

# ==============================
#Staff Leave
# ==============================
class StaffLeaveCreateModel(BaseModel):
    id: UUID
    company_code: str
    location_id: str
    staff_id: str
    leave_type: str
    date_from: datetime
    date_to: datetime
    part_of_day: str
    status: str
    reason: str
    approved_at: datetime
    approved_by: str
    is_active: bool = Field(None, description="default active is true")

class StaffLeaveUpdateModel(BaseModel):
    company_code: str
    location_id: str
    staff_id: str
    leave_type: str
    date_from: datetime
    date_to: datetime
    part_of_day: str
    status: str
    reason: str
    approved_at: datetime
    approved_by: str
    is_active: bool = Field(None, description="default active is true")


