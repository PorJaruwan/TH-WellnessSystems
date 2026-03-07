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
            # "company_code",
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
class CompanyResponse(BaseMasterResponse):
    # ✅ Company is the ONLY entity where company_code should be mapped to API field "code"
    code: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "code",
            "company_code",
        ),
    )

class DepartmentResponse(BaseMasterResponse): ...

class LocationResponse(BaseMasterResponse):
    # ✅ Location name must come from location_name
    name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("location_name", "name"),
    )


# class BuildingResponse(BaseMasterResponse): ...
class BuildingResponse(BaseMasterResponse):
    location_name: Optional[str] = None


class RoomResponse(BaseMasterResponse):
    # ✅ Room name must come from room_name
    name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("room_name", "name"),
    )

    location_name: Optional[str] = None
    building_name: Optional[str] = None
    type_name: Optional[str] = None

# class RoomResponse(BaseMasterResponse):

#     # ✅ override name mapping for Room entity
#     name: Optional[str] = Field(
#         default=None,
#         validation_alias=AliasChoices(
#             "room_name",
#             "name",
#         ),
#     )

#     location_name: Optional[str] = None
#     building_name: Optional[str] = None
#     type_name: Optional[str] = None

class RoomServiceResponse(BaseMasterResponse):
    room_name: Optional[str] = None
    service_name: Optional[str] = None

class RoomAvailabilityResponse(BaseMasterResponse):
    room_id: Optional[Any] = None
    room_name: Optional[str] = None

class ServiceResponse(BaseMasterResponse):
    service_type_name: Optional[str] = None

class ServiceTypeResponse(BaseMasterResponse): ...

class CountryResponse(BaseMasterResponse): ...

class ProvinceResponse(BaseMasterResponse):
    country_code: Optional[str] = None
    country_name_lo: Optional[str] = None
    country_name_en: Optional[str] = None

class CityResponse(BaseMasterResponse):
    province_name_lo: Optional[str] = None
    province_name_en: Optional[str] = None


class DistrictResponse(BaseMasterResponse):
    zip_code: Optional[int] = None
    city_id: Optional[int] = None
    city_name_lo: Optional[str] = None
    city_name_en: Optional[str] = None
    province_id: Optional[int] = None
    province_name_lo: Optional[str] = None
    province_name_en: Optional[str] = None

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


