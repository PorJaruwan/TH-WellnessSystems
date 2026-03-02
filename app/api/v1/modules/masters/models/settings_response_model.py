# app/api/v1/modules/masters/models/settings_response_model.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, AliasChoices
from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope


# =========================================================
# Shared
# =========================================================
class Paging(BaseModel):
    total: int
    limit: int
    offset: int


# =========================================================
# ✅ One Base for ALL masters (fix nulls globally)
# =========================================================
class BaseMasterResponse(BaseModel):
    """
    Masters response (patients-style) but supports legacy DB column names.

    Pydantic v2:
    - use AliasChoices for validation_alias
    """
    model_config = ConfigDict(
        from_attributes=True,
        extra="allow",
        populate_by_name=True,
    )

    # ✅ id may be UUID/int/str depending on table
    id: Optional[Any] = Field(
        default=None,
        validation_alias=AliasChoices(
            "id",
            "company_code",
            "country_code",
            "currency_code",
            "language_code",
        ),
    )

    # ✅ code mapping (API field = code)
    code: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "code",
            "company_code",
            "department_code",
            "location_code",
            "building_code",
            "room_code",
            "country_code",
            "currency_code",
            "language_code",
            "type_code",
        ),
    )

    # ✅ name mapping (API field = name)
    name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "name",
            "company_name",
            "department_name",
            "location_name",
            "building_name",
            "room_name",
            "service_name",
            "service_type_name",
            "currency_name",
            "language_name",
            "name_en",
            "name_lo",
        ),
    )

    is_active: Optional[bool] = Field(default=None, validation_alias=AliasChoices("is_active"))
    created_at: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("created_at"))
    updated_at: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("updated_at"))


# =========================================================
# Entity Responses (simple inherit)
# =========================================================
class CompanyResponse(BaseMasterResponse): ...
class DepartmentResponse(BaseMasterResponse): ...
class LocationResponse(BaseMasterResponse): ...
class BuildingResponse(BaseMasterResponse): ...
class RoomResponse(BaseMasterResponse): ...
class RoomServiceResponse(BaseMasterResponse): ...
class RoomAvailabilityResponse(BaseMasterResponse): ...

class ServiceResponse(BaseMasterResponse): ...
class ServiceTypeResponse(BaseMasterResponse): ...

class CountryResponse(BaseMasterResponse): ...
class ProvinceResponse(BaseMasterResponse): ...
class CityResponse(BaseMasterResponse): ...
class DistrictResponse(BaseMasterResponse): ...

class CurrencyResponse(BaseMasterResponse): ...
class LanguageResponse(BaseMasterResponse): ...
class GeographyResponse(BaseMasterResponse): ...


# =========================================================
# Envelope Aliases (match names used by *_envelopes/*.py)
# Keep payload as dict (compatible with ResponseHandler.success_from_request(data={...}))
# =========================================================

CompanySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
CompanyGetEnvelope: TypeAlias = SuccessEnvelope[dict]
CompanyCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
CompanyUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
CompanyDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

DepartmentSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
DepartmentGetEnvelope: TypeAlias = SuccessEnvelope[dict]
DepartmentCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
DepartmentUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
DepartmentDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

LocationSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
LocationGetEnvelope: TypeAlias = SuccessEnvelope[dict]
LocationCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
LocationUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
LocationDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

BuildingSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
BuildingGetEnvelope: TypeAlias = SuccessEnvelope[dict]
BuildingCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
BuildingUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
BuildingDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

RoomSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomGetEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

RoomServiceSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomServiceGetEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomServiceCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomServiceUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomServiceDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

RoomAvailabilitySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomAvailabilityGetEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomAvailabilityCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomAvailabilityUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
RoomAvailabilityDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

ServiceSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
ServiceGetEnvelope: TypeAlias = SuccessEnvelope[dict]
ServiceCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
ServiceUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
ServiceDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

ServiceTypeSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
ServiceTypeGetEnvelope: TypeAlias = SuccessEnvelope[dict]
ServiceTypeCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
ServiceTypeUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
ServiceTypeDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

CountrySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
CountryGetEnvelope: TypeAlias = SuccessEnvelope[dict]
CountryCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
CountryUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
CountryDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

ProvinceSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
ProvinceGetEnvelope: TypeAlias = SuccessEnvelope[dict]
ProvinceCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
ProvinceUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
ProvinceDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

CitySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
CityGetEnvelope: TypeAlias = SuccessEnvelope[dict]
CityCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
CityUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
CityDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

DistrictSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
DistrictGetEnvelope: TypeAlias = SuccessEnvelope[dict]
DistrictCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
DistrictUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
DistrictDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

CurrencySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
CurrencyGetEnvelope: TypeAlias = SuccessEnvelope[dict]
CurrencyCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
CurrencyUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
CurrencyDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

LanguageSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
LanguageGetEnvelope: TypeAlias = SuccessEnvelope[dict]
LanguageCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
LanguageUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
LanguageDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

GeographySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
GeographyGetEnvelope: TypeAlias = SuccessEnvelope[dict]
GeographyCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
GeographyUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
GeographyDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]


# # app/api/v1/modules/masters/models/settings_response_model.py
# from __future__ import annotations

# from datetime import datetime
# from typing import Any, Optional, TypeAlias
# from uuid import UUID

# from pydantic import BaseModel, ConfigDict

# from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope

# # =========================================================
# # Base / Shared
# # =========================================================

# class BaseMasterResponse(BaseModel):
#     """
#     ✅ Safe "patients-style" master response
#     - extra='allow' เพื่อไม่พัง แม้ field ใน DB/ORM จะเยอะกว่าที่ประกาศ
#     - from_attributes=True เพื่อ model_validate(orm_obj) ได้
#     """
#     model_config = ConfigDict(from_attributes=True, extra="allow")

#     id: Optional[UUID] = None
#     code: Optional[str] = None
#     name: Optional[str] = None
#     is_active: Optional[bool] = None
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class Paging(BaseModel):
#     total: int
#     limit: int
#     offset: int


# # =========================================================
# # Entity Responses (minimal + extra allow)
# # =========================================================

# class CompanyResponse(BaseMasterResponse): ...
# class DepartmentResponse(BaseMasterResponse): ...
# class LocationResponse(BaseMasterResponse): ...
# class BuildingResponse(BaseMasterResponse): ...
# class RoomResponse(BaseMasterResponse): ...
# class RoomServiceResponse(BaseMasterResponse): ...
# class RoomAvailabilityResponse(BaseMasterResponse): ...

# class ServiceResponse(BaseMasterResponse): ...
# class ServiceTypeResponse(BaseMasterResponse): ...

# class CountryResponse(BaseMasterResponse): ...
# class ProvinceResponse(BaseMasterResponse): ...
# class CityResponse(BaseMasterResponse): ...
# class DistrictResponse(BaseMasterResponse): ...

# class LanguageResponse(BaseMasterResponse): ...
# class CurrencyResponse(BaseMasterResponse): ...
# class GeographyResponse(BaseMasterResponse): ...


# # =========================================================
# # Envelope Aliases (match names used by *_envelopes/*.py)
# # We keep payload as dict to stay compatible with ResponseHandler success_from_request(data={...})
# # =========================================================

# # ---- Companies ----
# CompanySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# CompanyGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# CompanyCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# CompanyUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# CompanyDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Departments ----
# DepartmentSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# DepartmentGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# DepartmentCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# DepartmentUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# DepartmentDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Locations ----
# LocationSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# LocationGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# LocationCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# LocationUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# LocationDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Buildings ----
# BuildingSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# BuildingGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# BuildingCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# BuildingUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# BuildingDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Rooms ----
# RoomSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Room Services ----
# RoomServiceSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomServiceGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomServiceCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomServiceUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomServiceDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Room Availabilities ----
# RoomAvailabilitySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomAvailabilityGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomAvailabilityCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomAvailabilityUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# RoomAvailabilityDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Services ----
# ServiceSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# ServiceGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# ServiceCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# ServiceUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# ServiceDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Service Types ----
# ServiceTypeSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# ServiceTypeGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# ServiceTypeCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# ServiceTypeUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# ServiceTypeDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Countries ----
# CountrySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# CountryGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# CountryCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# CountryUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# CountryDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Provinces ----
# ProvinceSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# ProvinceGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# ProvinceCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# ProvinceUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# ProvinceDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Cities ----
# CitySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# CityGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# CityCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# CityUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# CityDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Districts ----
# DistrictSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# DistrictGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# DistrictCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# DistrictUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# DistrictDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Languages ----
# LanguageSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# LanguageGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# LanguageCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# LanguageUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# LanguageDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Currencies ----
# CurrencySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# CurrencyGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# CurrencyCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# CurrencyUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# CurrencyDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

# # ---- Geographies ----
# GeographySearchEnvelope: TypeAlias = SuccessEnvelope[dict]
# GeographyGetEnvelope: TypeAlias = SuccessEnvelope[dict]
# GeographyCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
# GeographyUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
# GeographyDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

