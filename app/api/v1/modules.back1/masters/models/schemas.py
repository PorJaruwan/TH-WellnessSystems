# app/api/v1/modules/masters/models/schemas.py
"""
WellPlus Standard:
- schemas.py = Request Models (Inbound) เท่านั้น
- Router ต้อง import Request จาก models.schemas
"""

from __future__ import annotations

# ✅ re-export request models (min-change patch)
from .settings_model import (  # noqa: F401
    _BaseIn,
    CompanyCreate,
    CompanyUpdate,
    LocationCreate,
    LocationUpdate,
    BuildingCreate,
    BuildingUpdate,
    RoomCreate,
    RoomUpdate,
    RoomServiceCreate,
    RoomServiceUpdate,
    RoomAvailabilityCreate,
    RoomAvailabilityUpdate,
    ServiceCreate,
    ServiceUpdate,
    ServiceTypeCreate,
    ServiceTypeUpdate,
    CountryCreate,
    CountryUpdate,
    ProvinceCreate,
    ProvinceUpdate,
    CityCreate,
    CityUpdate,
    DistrictCreate,
    DistrictUpdate,
    CurrencyCreate,
    CurrencyUpdate,
    LanguageCreate,
    LanguageUpdate,
    DepartmentCreate,
    DepartmentUpdate,
    GeographyCreate,
    GeographyUpdate,
)

__all__ = [
    "_BaseIn",
    "CompanyCreate", "CompanyUpdate",
    "LocationCreate", "LocationUpdate",
    "BuildingCreate", "BuildingUpdate",
    "RoomCreate", "RoomUpdate",
    "RoomServiceCreate", "RoomServiceUpdate",
    "RoomAvailabilityCreate", "RoomAvailabilityUpdate",
    "ServiceCreate", "ServiceUpdate",
    "ServiceTypeCreate", "ServiceTypeUpdate",
    "CountryCreate", "CountryUpdate",
    "ProvinceCreate", "ProvinceUpdate",
    "CityCreate", "CityUpdate",
    "DistrictCreate", "DistrictUpdate",
    "CurrencyCreate", "CurrencyUpdate",
    "LanguageCreate", "LanguageUpdate",
    "DepartmentCreate", "DepartmentUpdate",
    "GeographyCreate", "GeographyUpdate",
]