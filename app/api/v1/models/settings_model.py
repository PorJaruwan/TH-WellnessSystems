# app/api/v1/settings/setting_model.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

# ==============================
#Companies
# ==============================
class CompanyCreateModel(BaseModel):
    company_code: str
    company_name: str
    company_name_en: str
    address_line1: str
    address_line2: str
    address_line3: str
    address_line1_en: str
    address_line2_en: str
    address_line3_en: str
    post_code: str
    description: str
    telephone: str
    fax: str
    email: str
    domain_name: str
    tax_id: str
    vat_rate: float
    branch_id: str
    branch_name: str 
    head_office: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
class CompanyUpdateModel(BaseModel):
    company_name: str
    company_name_en: str
    address_line1: str
    address_line2: str
    address_line3: str
    address_line1_en: str
    address_line2_en: str
    address_line3_en: str
    post_code: str
    description: str
    telephone: str
    fax: str
    email: str
    domain_name: str
    tax_id: str
    vat_rate: float
    branch_id: str
    branch_name: str
    head_office: bool
    is_active: bool
    updated_at: datetime

# ==============================
#room_availabilities
# ==============================
class RoomAvailabilitiesCreateModel(BaseModel):
    id: UUID
    room_id: str
    available_date: datetime
    start_time: datetime
    end_time: datetime
    created_at: datetime
class RoomAvailabilitiesUpdateModel(BaseModel):
    room_id: str
    available_date: datetime
    start_time: datetime
    end_time: datetime
    created_at: datetime
class RoomAvailabilitiesResponseModel(BaseModel):
    id: UUID
    room_id: str
    available_date: datetime
    start_time: datetime
    end_time: datetime
    created_at: datetime
    
# ==============================
#rooms
# ==============================
class RoomsCreateModel(BaseModel):
    id: UUID
    room_name: str
    room_type: str
    capacity: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    room_code: str
    location_id: UUID
class RoomsUpdateModel(BaseModel):
    room_name: str
    room_type: str
    capacity: int
    is_available: bool
    updated_at: datetime
    room_code: str
    location_id: UUID
class RoomResponseModel(BaseModel):
    id: UUID
    room_name: str
    room_type: str
    capacity: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    room_code: str
    location_id: UUID

# ==============================
#room_services
# ==============================
class RoomServiceCreateModel(BaseModel):
    id: UUID
    room_id: str
    service_id: str
    is_default: bool
    created_at: datetime
class RoomServiceUpdateModel(BaseModel):
    room_id: str
    service_id: str
    is_default: bool

# ==============================
#services
# ==============================
class ServicesCreateModel(BaseModel):
    id: UUID
    service_name: str
    service_type_id: UUID
    duration: int
    service_price: float
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ServicesUpdateModel(BaseModel):
    service_name: str
    service_type_id: str
    duration: int
    service_price: float
    description: str
    is_active: bool
    updated_at: datetime

# ==============================
#service types
#===============================
class ServiceTypesCreateModel(BaseModel):
    id: UUID
    service_type_name: str
    description: str
    is_active: bool

class ServiceTypesUpdateModel(BaseModel):
    service_type_name: str
    description: str
    is_active: bool

# ==============================
#Cities
#===============================
class CityCreateModel(BaseModel):
    id: int
    name_lo: str
    name_en: str
    province_id: int
    country_code: str
    created_at: datetime
    updated_at: datetime

class CityUpdateModel(BaseModel):
    name_lo: str
    name_en: str
    province_id: Optional[int]
    country_code: str
    updated_at: datetime

# ==============================
#Countries
#===============================
class CountriesCreateModel(BaseModel):
    id: UUID
    name_lo: str
    name_en: str
    created_at: datetime
    updated_at: datetime

class CountriesUpdateModel(BaseModel):
    name_lo: str
    name_en: str
    updated_at: datetime

# ==============================
#Currencies
#===============================
class CurrenciesCreateModel(BaseModel):
    currency_code: str
    currency_name: str
    symbol: str
    decimal_places: int

class CurrenciesUpdateModel(BaseModel):
    currency_name: str
    symbol: str
    decimal_places: int


# ==============================
#Departments
#===============================
class DepartmentsCreateModel(BaseModel):
    id: UUID
    department_name: str
    description: str
    is_active: bool

class DepartmentsUpdateModel(BaseModel):
    department_name: str
    description: str
    is_active: bool



# ==============================
#District
#===============================
class DistrictCreateModel(BaseModel):
    id: int
    zip_code: int
    name_lo: str
    name_en: str
    city_id: int
    created_at: datetime
    updated_at: datetime

class DistrictUpdateModel(BaseModel):
    zip_code: int
    name_lo: str
    name_en: str
    city_id: Optional[int]
    updated_at: datetime


# ==============================
#Languages
#===============================
class LanguagesCreateModel(BaseModel):
    language_code: str
    language_name: str

class LanguagesUpdateModel(BaseModel):
    language_name: str


# ==============================
#Locations
#===============================
class LocationsCreateModel(BaseModel):
    id: UUID
    location_name: str
    company_code: str
    address: str
    phone: str
    email: str
    created_at: datetime
    updated_at: datetime

class LocationsUpdateModel(BaseModel):
    location_name: str
    company_code: str
    address: str
    phone: str
    email: str
    updated_at: datetime

# ==============================
#Buildings
#===============================
class BuildingsCreateModel(BaseModel):
    id: UUID
    company_code: str
    location_id: str
    building_code: str
    building_name: str
    floors: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    building_type: str
    reason: str

class BuildingsUpdateModel(BaseModel):
    company_code: str
    location_id: str
    building_code: str
    building_name: str
    floors: int
    is_active: bool
    updated_at: datetime
    building_type: str
    reason: str

# ==============================
#Provinces
#===============================
class ProvinceCreateModel(BaseModel):
    id: int
    name_lo: str
    name_en: str
    geography_id: int
    country_code: str
    created_at: datetime
    updated_at: datetime

class ProvinceUpdateModel(BaseModel):
    name_lo: str
    name_en: str
    geography_id: Optional[int]
    country_code: str
    updated_at: datetime
