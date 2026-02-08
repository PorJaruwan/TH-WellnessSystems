# app/api/v1/models/settings_response_model.py
# ✅ CLEAN VERSION (patients-style)
# - ✅ CHANGED: remove duplicated imports / duplicated Paging / duplicated Rooms section
# - ✅ CHANGED: keep a single RoomResponse that includes *_name fields
# - ✅ CHANGED: keep envelope patterns consistent: filters + paging + items list

from datetime import datetime, date, time
from typing import Any, Dict, List, Optional, TypeAlias
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.api.v1.models.bookings_model import SuccessEnvelope, ErrorEnvelope


# =========================================================
# Shared
# =========================================================
class Paging(BaseModel):
    """Standard paging block (patients-style)."""
    total: int
    limit: int
    offset: int


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

    tax_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CompanyOneData(BaseModel):
    company: CompanyResponse


class CompanyListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    companies: List[CompanyResponse]


class CompanyDeleteData(BaseModel):
    company_code: str


class CompanyCreateEnvelope(SuccessEnvelope[CompanyOneData]): ...
class CompanyGetEnvelope(SuccessEnvelope[CompanyOneData]): ...
class CompanyUpdateEnvelope(SuccessEnvelope[CompanyOneData]): ...
class CompanySearchEnvelope(SuccessEnvelope[CompanyListData]): ...
class CompanyDeleteEnvelope(SuccessEnvelope[CompanyDeleteData]): ...


# =========================================================
# Locations
# =========================================================
class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_code: Optional[str] = None  # ✅ keep safe for legacy rows
    location_code: Optional[str] = None
    location_name: Optional[str] = None

    is_active: bool
    created_at: datetime
    updated_at: datetime


class LocationOneData(BaseModel):
    location: LocationResponse


class LocationListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    locations: List[LocationResponse]


class LocationDeleteData(BaseModel):
    location_id: str


class LocationCreateEnvelope(SuccessEnvelope[LocationOneData]): ...
class LocationGetEnvelope(SuccessEnvelope[LocationOneData]): ...
class LocationUpdateEnvelope(SuccessEnvelope[LocationOneData]): ...
class LocationSearchEnvelope(SuccessEnvelope[LocationListData]): ...
class LocationDeleteEnvelope(SuccessEnvelope[LocationDeleteData]): ...


# =========================================================
# Buildings
# =========================================================
class BuildingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_code: Optional[str] = None  # ✅ keep safe for legacy rows
    building_code: Optional[str] = None
    building_name: Optional[str] = None

    location_id: Optional[UUID] = None
    location_name: Optional[str] = None # ✅ ADD THIS
    
    floors: Optional[int]
    
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BuildingOneData(BaseModel):
    building: BuildingResponse


class BuildingListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    buildings: List[BuildingResponse]


class BuildingDeleteData(BaseModel):
    building_id: str


class BuildingCreateEnvelope(SuccessEnvelope[BuildingOneData]): ...
class BuildingGetEnvelope(SuccessEnvelope[BuildingOneData]): ...
class BuildingUpdateEnvelope(SuccessEnvelope[BuildingOneData]): ...
class BuildingSearchEnvelope(SuccessEnvelope[BuildingListData]): ...
class BuildingDeleteEnvelope(SuccessEnvelope[BuildingDeleteData]): ...


# =========================================================
# Departments
# =========================================================
class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_code: Optional[str] = None  # ✅ safer for legacy rows

    department_code: Optional[str] = None  # ✅ allow null (align with create/update reality)
    department_name: Optional[str] = None  # ✅ safer if legacy rows

    is_active: bool
    created_at: datetime
    updated_at: datetime


class DepartmentOneData(BaseModel):
    department: DepartmentResponse


class DepartmentListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    departments: List[DepartmentResponse]


class DepartmentDeleteData(BaseModel):
    department_id: str


class DepartmentCreateEnvelope(SuccessEnvelope[DepartmentOneData]): ...
class DepartmentGetEnvelope(SuccessEnvelope[DepartmentOneData]): ...
class DepartmentUpdateEnvelope(SuccessEnvelope[DepartmentOneData]): ...
class DepartmentSearchEnvelope(SuccessEnvelope[DepartmentListData]): ...
class DepartmentDeleteEnvelope(SuccessEnvelope[DepartmentDeleteData]): ...


# ==========================================================
# Rooms (Response)
# ==========================================================
class RoomResponse(BaseModel):
    """
    Rooms response (patients-style)

    ✅ CHANGED:
    - include location_name/building_name/room_type_name
      (these are computed properties on ORM Room)
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    room_code: Optional[str] = None
    room_name: Optional[str] = None

    location_id: Optional[UUID] = None
    location_name: Optional[str] = None
    
    building_id: Optional[UUID] = None
    building_name: Optional[str] = None

    room_type_id: Optional[UUID] = None
    room_type_name: Optional[str] = None

    floor_number: Optional[int] = None
    capacity: Optional[int] = None
    is_available: Optional[bool] = None

    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoomOneData(BaseModel):
    room: RoomResponse


class RoomListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    rooms: List[RoomResponse]


class RoomDeleteData(BaseModel):
    room_id: str


class RoomCreateEnvelope(SuccessEnvelope[RoomOneData]): ...
class RoomGetEnvelope(SuccessEnvelope[RoomOneData]): ...
class RoomUpdateEnvelope(SuccessEnvelope[RoomOneData]): ...
class RoomSearchEnvelope(SuccessEnvelope[RoomListData]): ...
class RoomDeleteEnvelope(SuccessEnvelope[RoomDeleteData]): ...


# ✅ REMOVED DUPLICATE:
# - The original file contained a duplicated "Rooms" section with repeated imports + Paging + RoomResponse.
# - Keeping only one canonical definition prevents class override issues.


# =========================================================
# Room Services
# =========================================================
class RoomServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    room_id: UUID
    room_name: Optional[str] = None

    service_id: UUID
    service_name: Optional[str] = None

    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoomServiceOneData(BaseModel):
    room_service: RoomServiceResponse


class RoomServiceListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    room_services: List[RoomServiceResponse]


class RoomServiceDeleteData(BaseModel):
    room_service_id: str


class RoomServiceCreateEnvelope(SuccessEnvelope[RoomServiceOneData]): ...
class RoomServiceGetEnvelope(SuccessEnvelope[RoomServiceOneData]): ...
class RoomServiceUpdateEnvelope(SuccessEnvelope[RoomServiceOneData]): ...
class RoomServiceSearchEnvelope(SuccessEnvelope[RoomServiceListData]): ...
class RoomServiceDeleteEnvelope(SuccessEnvelope[RoomServiceDeleteData]): ...


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
    updated_at: Optional[datetime] = None


class RoomAvailabilityOneData(BaseModel):
    room_availability: RoomAvailabilityResponse


class RoomAvailabilityListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    room_availabilities: List[RoomAvailabilityResponse]


class RoomAvailabilityDeleteData(BaseModel):
    room_availability_id: str


class RoomAvailabilityCreateEnvelope(SuccessEnvelope[RoomAvailabilityOneData]): ...
class RoomAvailabilityGetEnvelope(SuccessEnvelope[RoomAvailabilityOneData]): ...
class RoomAvailabilityUpdateEnvelope(SuccessEnvelope[RoomAvailabilityOneData]): ...
class RoomAvailabilitySearchEnvelope(SuccessEnvelope[RoomAvailabilityListData]): ...
class RoomAvailabilityDeleteEnvelope(SuccessEnvelope[RoomAvailabilityDeleteData]): ...


# =========================================================
# Geography: Countries / Provinces / Cities / Districts
# =========================================================
class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    country_code: str
    name_lo: str
    name_en: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CountryOneData(BaseModel):
    country: CountryResponse


class CountryListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    countries: List[CountryResponse]


class CountryDeleteData(BaseModel):
    country_code: str


class CountryCreateEnvelope(SuccessEnvelope[CountryOneData]): ...
class CountryGetEnvelope(SuccessEnvelope[CountryOneData]): ...
class CountryUpdateEnvelope(SuccessEnvelope[CountryOneData]): ...
class CountrySearchEnvelope(SuccessEnvelope[CountryListData]): ...
class CountryDeleteEnvelope(SuccessEnvelope[CountryDeleteData]): ...


class ProvinceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name_lo: str
    name_en: str
    geography_id: Optional[int] = None
    country_code: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProvinceOneData(BaseModel):
    province: ProvinceResponse


class ProvinceListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    provinces: List[ProvinceResponse]


class ProvinceDeleteData(BaseModel):
    province_id: str


class ProvinceCreateEnvelope(SuccessEnvelope[ProvinceOneData]): ...
class ProvinceGetEnvelope(SuccessEnvelope[ProvinceOneData]): ...
class ProvinceUpdateEnvelope(SuccessEnvelope[ProvinceOneData]): ...
class ProvinceSearchEnvelope(SuccessEnvelope[ProvinceListData]): ...
class ProvinceDeleteEnvelope(SuccessEnvelope[ProvinceDeleteData]): ...

class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name_lo: str
    name_en: str

    province_id: int
    province_name_lo: Optional[str] = None
    province_name_en: Optional[str] = None

    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



class CityOneData(BaseModel):
    city: CityResponse


class CityListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    cities: List[CityResponse]


class CityDeleteData(BaseModel):
    city_id: str


class CityCreateEnvelope(SuccessEnvelope[CityOneData]): ...
class CityGetEnvelope(SuccessEnvelope[CityOneData]): ...
class CityUpdateEnvelope(SuccessEnvelope[CityOneData]): ...
class CitySearchEnvelope(SuccessEnvelope[CityListData]): ...
class CityDeleteEnvelope(SuccessEnvelope[CityDeleteData]): ...


class DistrictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zip_code: int
    name_lo: str
    name_en: str
    city_id: int

    # ✅ CHANGED: city display fields
    city_name_lo: Optional[str] = None
    city_name_en: Optional[str] = None

    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



class DistrictOneData(BaseModel):
    district: DistrictResponse


class DistrictListData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    districts: List[DistrictResponse]


class DistrictDeleteData(BaseModel):
    district_id: str


class DistrictCreateEnvelope(SuccessEnvelope[DistrictOneData]): ...
class DistrictGetEnvelope(SuccessEnvelope[DistrictOneData]): ...
class DistrictUpdateEnvelope(SuccessEnvelope[DistrictOneData]): ...
class DistrictSearchEnvelope(SuccessEnvelope[DistrictListData]): ...
class DistrictDeleteEnvelope(SuccessEnvelope[DistrictDeleteData]): ...


# =========================================================
# Services
# =========================================================
class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_name: str
    service_type_id: UUID
    service_type_name: Optional[str] = None
    service_price: Optional[float] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ServiceSearchData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    services: List[ServiceResponse]


class ServiceByIdData(BaseModel):
    service: ServiceResponse


class ServiceCreateData(BaseModel):
    service: ServiceResponse


class ServiceUpdateData(BaseModel):
    service: ServiceResponse


class ServiceDeleteData(BaseModel):
    service_id: str


# ✅ NOTE:
# Some modules in your codebase use TypeAlias union with ErrorEnvelope.
# Keeping it as-is to match current usage style.
ServiceSearchEnvelope: TypeAlias = SuccessEnvelope[ServiceSearchData] | ErrorEnvelope
ServiceByIdEnvelope: TypeAlias = SuccessEnvelope[ServiceByIdData] | ErrorEnvelope
ServiceCreateEnvelope: TypeAlias = SuccessEnvelope[ServiceCreateData] | ErrorEnvelope
ServiceUpdateEnvelope: TypeAlias = SuccessEnvelope[ServiceUpdateData] | ErrorEnvelope
ServiceDeleteEnvelope: TypeAlias = SuccessEnvelope[ServiceDeleteData] | ErrorEnvelope


# =========================================================
# Service Types
# =========================================================
class ServiceTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_type_name: str

    description: Optional[str] = None
    is_active: Optional[bool] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ServiceTypeSearchData(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    service_types: List[ServiceTypeResponse]


class ServiceTypeByIdData(BaseModel):
    service_type: ServiceTypeResponse


class ServiceTypeCreateData(BaseModel):
    service_type: ServiceTypeResponse


class ServiceTypeUpdateData(BaseModel):
    service_type: ServiceTypeResponse


class ServiceTypeDeleteData(BaseModel):
    service_type_id: str


ServiceTypeSearchEnvelope: TypeAlias = SuccessEnvelope[ServiceTypeSearchData] | ErrorEnvelope
ServiceTypeByIdEnvelope: TypeAlias = SuccessEnvelope[ServiceTypeByIdData] | ErrorEnvelope
ServiceTypeCreateEnvelope: TypeAlias = SuccessEnvelope[ServiceTypeCreateData] | ErrorEnvelope
ServiceTypeUpdateEnvelope: TypeAlias = SuccessEnvelope[ServiceTypeUpdateData] | ErrorEnvelope
ServiceTypeDeleteEnvelope: TypeAlias = SuccessEnvelope[ServiceTypeDeleteData] | ErrorEnvelope
