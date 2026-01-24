# app/api/v1/models/settings_response_model.py  (ADD)

from __future__ import annotations

from datetime import datetime, date, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# =========================================================
# Companies
# =========================================================
class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_code: str
    company_name: str
    company_name_en: str

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None
    address_line1_en: Optional[str] = None
    address_line2_en: Optional[str] = None
    address_line3_en: Optional[str] = None
    post_code: Optional[str] = None
    description: Optional[str] = None
    telephone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    domain_name: Optional[str] = None
    tax_id: Optional[str] = None

    vat_rate: float
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None
    head_office: Optional[bool] = None
    is_active: bool
    company_type: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Locations
# =========================================================
class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_code: str
    location_name: str
    location_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    location_code: Optional[str] = None
    manager_id: Optional[UUID] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Buildings
# =========================================================
class BuildingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_code: str
    location_id: UUID
    building_code: str
    building_name: str
    floors: Optional[int] = None
    is_active: bool
    building_type: Optional[str] = None
    reason: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =========================================================
# Service Types
# =========================================================
class ServiceTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_type_name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# =========================================================
# Services
# =========================================================
class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_name: str
    service_type_id: UUID
    service_price: float
    duration: int
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# =========================================================
# Departments
# =========================================================
class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_code: str
    department_name: str
    is_active: bool
    department_code: Optional[str] = None
    department_type_id: Optional[UUID] = None
    head_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


# =========================================================
# Rooms
# =========================================================
class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    location_id: UUID
    building_id: UUID
    room_code: str
    room_name: str
    capacity: int
    is_available: bool
    is_active: bool
    room_type_id: Optional[UUID] = None
    floor_number: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# =========================================================
# Room Services
# =========================================================
class RoomServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    room_id: UUID
    service_id: UUID
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


# =========================================================
# Room Availabilities
# =========================================================
class RoomAvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    room_id: UUID

    available_date: date
    start_time: time
    end_time: time

    created_at: datetime
