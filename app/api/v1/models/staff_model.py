# app/api/v1/settings/setting_model.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

# ==============================
#Staff
# ==============================
class StaffCreateModel(BaseModel):
    id: UUID
    staff_name: str
    role: str
    specialty: str
    phone: str
    email: str
    created_at: datetime
    updated_at: datetime

class StaffUpdateModel(BaseModel):
    staff_name: str
    role: str
    specialty: str
    phone: str
    email: str
    created_at: datetime
    updated_at: datetime
    #deleted_at: datetime

# ==============================
#Staff Services
# ==============================
class StaffServicesCreateModel(BaseModel):
    id: UUID
    staff_id: str
    service_id: str
    duration_minutes: int

class StaffServicesUpdateModel(BaseModel):
    staff_id: str
    service_id: str
    duration_minutes: int


# ==============================
#Staff Locations
# ==============================
class StaffLocationsCreateModel(BaseModel):
    id: UUID
    staff_id: str
    location_id: str

class StaffLocationsUpdateModel(BaseModel):
    staff_id: str
    location_id: str


# ==============================
#Staff Departments
# ==============================
class StaffDepartmentsCreateModel(BaseModel):
    id: UUID
    staff_id: str
    department_id: str

class StaffDepartmentsUpdateModel(BaseModel):
    staff_id: str
    department_id: str
