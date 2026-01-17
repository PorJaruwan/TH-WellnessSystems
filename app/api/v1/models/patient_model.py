# app/api/v1/models/patients_model.py
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from enum import Enum

# ==========================================================
# Patients (Standard: Create / Update / Read)
# ==========================================================
class SexEnum(str, Enum):
    male = "male"
    female = "female"
    lgbtq = "lgbtq"


class MainContactMethodEnum(str, Enum):
    phone = "phone"
    email = "email"
    text = "text"


class PatientBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # --- Required ---
    patient_code: str = Field(..., max_length=50)
    first_name_lo: str = Field(..., max_length=100)
    last_name_lo: str = Field(..., max_length=100)
    id_card_no: str = Field(..., max_length=25)
    email: EmailStr
    payment_status: str = Field(..., max_length=25)
    full_name_lo: str = Field(..., max_length=255)

    # --- Optional ---
    title_en: Optional[str] = Field(None, max_length=25)
    first_name_en: Optional[str] = Field(None, max_length=100)
    last_name_en: Optional[str] = Field(None, max_length=100)

    title_lo: Optional[str] = Field(None, max_length=25)
    title_cc: Optional[str] = Field(None, max_length=25)

    social_security_id: Optional[str] = Field(None, max_length=25)
    sex: Optional[SexEnum] = None
    birth_date: Optional[date] = None
    religion: Optional[str] = Field(None, max_length=255)

    profession_id: Optional[UUID] = None
    patient_type_id: Optional[UUID] = None

    telephone: Optional[str] = Field(None, max_length=25)
    work_phone: Optional[str] = Field(None, max_length=25)

    line_id: Optional[str] = Field(None, max_length=100)
    facebook: Optional[str] = Field(None, max_length=100)
    whatsapp: Optional[str] = Field(None, max_length=100)

    allergy_id: Optional[UUID] = None
    drug_allergy_id: Optional[UUID] = None
    allergy_note: Optional[str] = None

    customer_profile_id: Optional[UUID] = None

    contact_first_name: Optional[str] = Field(None, max_length=100)
    contact_last_name: Optional[str] = Field(None, max_length=100)
    contact_phone1: Optional[str] = Field(None, max_length=25)
    contact_phone2: Optional[str] = Field(None, max_length=25)

    # ✅ ใช้ชื่อเดียวกับ ORM
    contact_relationship: Optional[str] = Field(
        default=None,
        validation_alias="relationship",   # client ยังส่ง relationship ได้
    )

    alert_id: Optional[UUID] = None
    alert_note: Optional[str] = None

    salesperson_id: Optional[UUID] = None
    marketing_person_id: Optional[UUID] = None

    locations_id: Optional[UUID] = None
    source_id: Optional[UUID] = None

    patient_note: Optional[str] = None
    status: Optional[str] = Field(None, max_length=25)

    is_active: bool = True

    full_name_en: Optional[str] = Field(None, max_length=255)
    main_contact_method: Optional[MainContactMethodEnum] = None


class PatientCreate(PatientBase):
    """POST /patients"""
    pass


class PatientUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    patient_code: Optional[str] = Field(None, max_length=50)

    title_en: Optional[str] = Field(None, max_length=25)
    first_name_en: Optional[str] = Field(None, max_length=100)
    last_name_en: Optional[str] = Field(None, max_length=100)

    title_lo: Optional[str] = Field(None, max_length=25)
    first_name_lo: Optional[str] = Field(None, max_length=100)
    last_name_lo: Optional[str] = Field(None, max_length=100)

    id_card_no: Optional[str] = Field(None, max_length=25)
    sex: Optional[SexEnum] = None
    birth_date: Optional[date] = None

    email: Optional[EmailStr] = None
    payment_status: Optional[str] = Field(None, max_length=25)

    contact_relationship: Optional[str] = Field(
        default=None,
        validation_alias="relationship",
    )

    is_active: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=25)


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime



# ==========================================================
# Other schemas (คงไว้ตามไฟล์เดิม เพื่อไม่กระทบ modules อื่น)
# ==========================================================

# ==============================
# sources
# ==============================
class SourcesCreateModel(BaseModel):
    id: UUID
    source_name: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SourcesUpdateModel(BaseModel):
    source_name: str
    description: str
    is_active: bool
    updated_at: datetime


# ==============================
# alerts
# ==============================
class AlertCreateModel(BaseModel):
    id: UUID
    alert_type: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AlertUpdateModel(BaseModel):
    alert_type: str
    description: str
    is_active: bool
    updated_at: datetime


# ==============================
# allergies
# ==============================
class AllergyCreateModel(BaseModel):
    id: UUID
    allergy_name: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    allergy_type: str


class AllergyUpdateModel(BaseModel):
    allergy_name: str
    description: str
    is_active: bool
    updated_at: datetime
    allergy_type: str


# ==============================
# marketing staff
# ==============================
class MarketingStaffCreateModel(BaseModel):
    id: UUID
    marketing_name: str
    campaign: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MarketingStaffUpdateModel(BaseModel):
    marketing_name: str
    campaign: str
    is_active: bool
    updated_at: datetime


# ==============================
# patient addresses
# ==============================
class AddressesCreateModel(BaseModel):
    patient_id: str
    address_type: str
    address_line1: str
    address_line2: str
    sub_district: str
    city: str
    state: str
    postal_code: str
    country_code: str
    full_address_lo: str
    full_address_en: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class AddressesUpdateModel(BaseModel):
    address_line1: str
    address_line2: str
    sub_district: str
    city: str
    state: str
    postal_code: str
    country_code: str
    full_address_lo: str
    full_address_en: str
    is_primary: bool
    updated_at: datetime


# ==============================
# patient images
# ==============================
class PatientImageCreateModel(BaseModel):
    id: UUID
    patient_id: UUID
    file_path: Optional[str]
    image_type: str
    description: str
    created_at: datetime
    updated_at: datetime


class PatientImageUpdateModel(BaseModel):
    file_path: Optional[str] = Field(None, description="URL file path image")
    image_type: Optional[str] = Field(None, description="Image type (e.g. JPEG)")
    description: Optional[str] = Field(None, description="Additional note")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")


# ==============================
# patient types
# ==============================
class PatientTypeCreateModel(BaseModel):
    id: UUID
    type_name: str
    description: str
    is_active: str
    created_at: datetime
    updated_at: datetime


class PatientTypeUpdateModel(BaseModel):
    type_name: str
    description: str
    is_active: str
    updated_at: datetime


# ==============================
# sale staff
# ==============================
class SaleStaffCreateModel(BaseModel):
    id: UUID
    sale_person_name: str
    department_name: str
    is_active: str
    created_at: datetime
    updated_at: datetime


class SaleStaffUpdateModel(BaseModel):
    sale_person_name: str
    department_name: str
    is_active: str
    updated_at: datetime
