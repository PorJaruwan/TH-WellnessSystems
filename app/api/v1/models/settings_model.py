# app/api/v1/models/settings_model.py

from __future__ import annotations

from datetime import datetime, date, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

# =========================================================
# Base: normalize input ("" -> None), strip strings
# =========================================================
class _BaseIn(BaseModel):
    """
    Shared input base model for Create/Update schemas.
    - strip whitespace on all strings
    - convert empty strings "" to None (before validation)
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("*", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


# =========================================================
# Companies
# =========================================================
class CompanyCreate(_BaseIn):
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

    vat_rate: float = 0
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None
    head_office: Optional[bool] = False
    is_active: Optional[bool] = True
    company_type: Optional[str] = Field(
        None, description="check: Hospital Group, Clinic Chain, Wellness Center, Partner"
    )


class CompanyUpdate(_BaseIn):
    company_name: Optional[str] = None
    company_name_en: Optional[str] = None

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

    vat_rate: Optional[float] = None
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None
    head_office: Optional[bool] = None
    is_active: Optional[bool] = None
    company_type: Optional[str] = Field(
        None, description="check: Hospital Group, Clinic Chain, Wellness Center, Partner"
    )


# =========================================================
# Locations
# =========================================================
class LocationCreate(_BaseIn):
    id: Optional[UUID] = None  # DB default gen_random_uuid()
    company_code: str = Field(..., description="foreign key: companies.company_code")
    location_name: str = Field(..., description="location name")

    location_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    is_active: Optional[bool] = True
    location_code: Optional[str] = None
    manager_id: Optional[UUID] = Field(None, description="foreign key: staff.id (optional)")

    # server managed in DB; keep optional to avoid client forcing values
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LocationUpdate(_BaseIn):
    location_name: Optional[str] = None
    location_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    location_code: Optional[str] = None
    manager_id: Optional[UUID] = None


# =========================================================
# Buildings
# =========================================================
class BuildingCreate(_BaseIn):
    id: Optional[UUID] = None  # DB default gen_random_uuid()
    company_code: str
    location_id: UUID

    building_code: str
    building_name: str

    floors: Optional[int] = None
    is_active: Optional[bool] = True
    building_type: Optional[str] = Field(
        None, description="check: clinical, service, facility, office, lab, ward, other"
    )
    reason: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BuildingUpdate(_BaseIn):
    company_code: Optional[str] = None
    location_id: Optional[UUID] = None
    building_code: Optional[str] = None
    building_name: Optional[str] = None
    floors: Optional[int] = None
    is_active: Optional[bool] = None
    building_type: Optional[str] = None
    reason: Optional[str] = None


# =========================================================
# Rooms
# =========================================================
class RoomCreate(_BaseIn):
    id: Optional[UUID] = None
    location_id: UUID
    building_id: UUID

    room_code: str
    room_name: str
    capacity: int = 1

    is_available: Optional[bool] = True
    is_active: Optional[bool] = True

    room_type_id: Optional[UUID] = Field(None, description="select from room_type table (optional)")
    floor_number: Optional[int] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoomUpdate(_BaseIn):
    location_id: Optional[UUID] = None
    building_id: Optional[UUID] = None
    room_code: Optional[str] = None
    room_name: Optional[str] = None
    capacity: Optional[int] = None
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None
    room_type_id: Optional[UUID] = None
    floor_number: Optional[int] = None


# =========================================================
# Room Services
# =========================================================
class RoomServiceCreate(_BaseIn):
    id: Optional[UUID] = None
    room_id: UUID
    service_id: UUID
    is_default: Optional[bool] = False
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoomServiceUpdate(_BaseIn):
    room_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


# =========================================================
# Room Availabilities
# =========================================================
class RoomAvailabilityCreate(_BaseIn):
    id: Optional[UUID] = None
    room_id: UUID
    available_date: date
    start_time: time
    end_time: time
    created_at: Optional[datetime] = None


class RoomAvailabilityUpdate(_BaseIn):
    room_id: Optional[UUID] = None
    available_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


# =========================================================
# Services
# =========================================================
class ServiceCreate(_BaseIn):
    id: Optional[UUID] = None
    service_name: str
    service_type_id: UUID
    service_price: float
    duration: int

    description: Optional[str] = None
    is_active: Optional[bool] = True

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ServiceUpdate(_BaseIn):
    service_name: Optional[str] = None
    service_type_id: Optional[UUID] = None
    service_price: Optional[float] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# =========================================================
# Service Types
# =========================================================
class ServiceTypeCreate(_BaseIn):
    id: Optional[UUID] = None
    service_type_name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ServiceTypeUpdate(_BaseIn):
    service_type_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# =========================================================
# Countries
# =========================================================
class CountryCreate(_BaseIn):
    id: Optional[UUID] = None
    name_lo: str
    name_en: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CountryUpdate(_BaseIn):
    name_lo: Optional[str] = None
    name_en: Optional[str] = None


# =========================================================
# Provinces
# =========================================================
class ProvinceCreate(_BaseIn):
    id: Optional[int] = None
    name_lo: str
    name_en: str
    geography_id: Optional[int] = None
    country_code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProvinceUpdate(_BaseIn):
    name_lo: Optional[str] = None
    name_en: Optional[str] = None
    geography_id: Optional[int] = None
    country_code: Optional[str] = None


# =========================================================
# Cities
# =========================================================
class CityCreate(_BaseIn):
    id: Optional[int] = None
    name_lo: str
    name_en: str
    province_id: int
    country_code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CityUpdate(_BaseIn):
    name_lo: Optional[str] = None
    name_en: Optional[str] = None
    province_id: Optional[int] = None
    country_code: Optional[str] = None


# =========================================================
# Districts
# =========================================================
class DistrictCreate(_BaseIn):
    id: Optional[int] = None
    zip_code: int
    name_lo: str
    name_en: str
    city_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DistrictUpdate(_BaseIn):
    zip_code: Optional[int] = None
    name_lo: Optional[str] = None
    name_en: Optional[str] = None
    city_id: Optional[int] = None


# =========================================================
# Currencies
# =========================================================
class CurrencyCreate(_BaseIn):
    currency_code: str
    currency_name: str
    symbol: Optional[str] = None
    decimal_places: int = 2


class CurrencyUpdate(_BaseIn):
    currency_name: Optional[str] = None
    symbol: Optional[str] = None
    decimal_places: Optional[int] = None


# =========================================================
# Languages
# =========================================================
class LanguageCreate(_BaseIn):
    language_code: str
    language_name: str


class LanguageUpdate(_BaseIn):
    language_name: Optional[str] = None


# =========================================================
# Departments
# =========================================================
class DepartmentCreate(_BaseIn):
    id: Optional[UUID] = None
    company_code: str = Field(..., description="foreign key: companies.company_code")
    department_name: str
    is_active: Optional[bool] = True
    department_code: Optional[str] = Field(None, description="unique: company_code + department_code")
    department_type_id: Optional[UUID] = Field(None, description="foreign key: department type id")
    head_id: Optional[UUID] = Field(None, description="foreign key: staff id")


class DepartmentUpdate(_BaseIn):
    department_name: Optional[str] = None
    is_active: Optional[bool] = None
    department_code: Optional[str] = None
    department_type_id: Optional[UUID] = None
    head_id: Optional[UUID] = None
