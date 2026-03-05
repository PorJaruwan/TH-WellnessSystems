# app/api/v1/modules/masters/models/dtos.py
from __future__ import annotations

from app.api.v1.modules.masters.models.settings_response_model import (
    CompanyResponse,
    DepartmentResponse,
    LocationResponse,
    BuildingResponse,
    RoomResponse,
    RoomServiceResponse,
    RoomAvailabilityResponse,
    ServiceResponse,
    ServiceTypeResponse,
    CountryResponse,
    ProvinceResponse,
    CityResponse,
    DistrictResponse,
    LanguageResponse,
    CurrencyResponse,
    GeographyResponse,
)

__all__ = [
    "CompanyResponse",
    "DepartmentResponse",
    "LocationResponse",
    "BuildingResponse",
    "RoomResponse",
    "RoomServiceResponse",
    "RoomAvailabilityResponse",
    "ServiceResponse",
    "ServiceTypeResponse",
    "CountryResponse",
    "ProvinceResponse",
    "CityResponse",
    "DistrictResponse",
    "LanguageResponse",
    "CurrencyResponse",
    "GeographyResponse",
]

# # --- backward compatible aliases (optional) ---
# CompanyDTO = CompanyResponse
# DepartmentDTO = DepartmentResponse
# LocationDTO = LocationResponse
# BuildingDTO = BuildingResponse
# RoomDTO = RoomResponse
# RoomServiceDTO = RoomServiceResponse
# RoomAvailabilityDTO = RoomAvailabilityResponse
# ServiceDTO = ServiceResponse
# ServiceTypeDTO = ServiceTypeResponse
# CountryDTO = CountryResponse
# ProvinceDTO = ProvinceResponse
# CityDTO = CityResponse
# DistrictDTO = DistrictResponse

# __all__ += [
#     "CompanyDTO",
#     "DepartmentDTO",
#     "LocationDTO",
#     "BuildingDTO",
#     "RoomDTO",
#     "RoomServiceDTO",
#     "RoomAvailabilityDTO",
#     "ServiceDTO",
#     "ServiceTypeDTO",
#     "CountryDTO",
#     "ProvinceDTO",
#     "CityDTO",
#     "DistrictDTO",
# ]