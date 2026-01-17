# app/api/v1/settings/setting_model.py
from pydantic import BaseModel, Field
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
    is_active: bool = Field(None, description="default true")
    company_type: Optional[str] = Field(None, description="check: Hospital Group, Clinic Chain, Wellness Center, Partner")

class CompanyUpdateModel(BaseModel):
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
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
    company_type: Optional[str] = Field(None, description="check: Hospital Group, Clinic Chain, Wellness Center, Partner")

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
    location_id: str
    building_id: str
    room_code: str
    room_name: str
    capacity: int
    is_available: bool
    is_active: bool
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
    room_type_id: str = Field(None, description="select from room_type table")
    floor_number: int
class RoomsUpdateModel(BaseModel):
    location_id: str
    building_id: str
    room_code: str
    room_name: str
    capacity: int
    is_available: bool
    is_active: bool
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
    room_type_id: str = Field(None, description="select from room_type table")
    floor_number: int
class RoomResponseModel(BaseModel):
    id: UUID
    location_id: str
    building_id: str
    room_code: str
    room_name: str
    capacity: int
    is_available: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    room_type_id: str
    floor_number: int

# ==============================
#room_services
# ==============================
class RoomServiceCreateModel(BaseModel):
    id: UUID
    room_id: str
    service_id: str
    is_default: bool = Field(None, description="default false")
    is_active: bool = Field(None, description="default true")
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
class RoomServiceUpdateModel(BaseModel):
    room_id: str
    service_id: str
    is_default: bool = Field(None, description="default false")
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

# ==============================
#services
# ==============================
class ServicesCreateModel(BaseModel):
    id: UUID
    service_name: str
    service_type_id: UUID
    service_price: float
    duration: int
    description: Optional[str] = Field(None, description="Additional note")
    is_active: bool = Field(None, description="default true")
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

class ServicesUpdateModel(BaseModel):
    service_name: str
    service_type_id: UUID
    service_price: float
    duration: int
    description: Optional[str] = Field(None, description="Additional note")
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

# ==============================
#service types
#===============================
class ServiceTypesCreateModel(BaseModel):
    id: UUID
    service_type_name: str
    description: Optional[str] = Field(None, description="Additional note")
    is_active: bool = Field(None, description="default true")
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

class ServiceTypesUpdateModel(BaseModel):
    service_type_name: str
    description: Optional[str] = Field(None, description="Additional note")
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")

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
    company_code: str = Field(None, description="foreign key: company code")
    department_name: str
    is_active: bool = Field(None, description="default true")
    department_code: str = Field(None, description="unique: company code + department code")
    department_type_id: Optional[str] = Field(None, description="foreign key: department type id")
    head_id: Optional[str] = Field(None, description="foreign key: staff id")

class DepartmentsUpdateModel(BaseModel):
    department_name: str
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
    department_type_id: Optional[str] = Field(None, description="foreign key: department type id")
    head_id: Optional[str] = Field(None, description="foreign key: staff id")

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
    company_code: str = Field(None, description="foreign key: company code")
    location_name: str = Field(None, description="unique: company code + location code")
    location_type: str
    address: str
    phone: str
    email: str
    is_active: bool = Field(None, description="default true")
    created_at: Optional[datetime] = Field(None, description="Timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
    location_code: str 
    manager_id: Optional[str] = Field(None, description="foreign key: staff id")

class LocationsUpdateModel(BaseModel):
    location_name: str = Field(None, description="unique: company code + location code")
    location_type: str
    address: str
    phone: str
    email: str
    is_active: bool = Field(None, description="default true")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")
    location_code: str 
    manager_id: Optional[str] = Field(None, description="foreign key: staff id")

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
