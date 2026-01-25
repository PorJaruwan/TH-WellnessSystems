# Pydantic schema
# app/api/v1/models/patients_model.py

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from enum import Enum


# =========================================================
# Common base
# =========================================================

class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)



###=====Patient-master=====###
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
    #payment_status: str = Field(..., max_length=25)
    status: str = Field(..., max_length=25)
    #full_name_lo: str = Field(..., max_length=255)

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

    #full_name_en: Optional[str] = Field(None, max_length=255)
    main_contact_method: Optional[MainContactMethodEnum] = None

    alert_level: Optional[str] = None
    critical_medical_note: Optional[str] = None

    market_source_id: Optional[UUID] = None            # ✅ NEW
    referral_source_note: Optional[str] = Field(None, max_length=500)  # ✅ NEW
    market_source_note: Optional[str] = Field(None, max_length=500)    # ✅ NEW


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

    market_source_id: Optional[UUID] = None            # ✅ NEW
    referral_source_note: Optional[str] = Field(None, max_length=500)  # ✅ NEW
    market_source_note: Optional[str] = Field(None, max_length=500)    # ✅ NEW


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    full_name_lo: str = Field(..., max_length=255)
    full_name_en: Optional[str] = Field(None, max_length=255)

###=====Patient-child=====###
# =========================================================
# Patient Addresses
# =========================================================
# ใช้ composite key: (patient_id, address_type)

class PatientAddressBase(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    sub_district: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None
    full_address_lo: Optional[str] = None
    full_address_en: Optional[str] = None
    is_primary: bool = False


class PatientAddressCreate(PatientAddressBase):
    patient_id: UUID
    address_type: str


class PatientAddressUpdate(BaseModel):
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    sub_district: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: Optional[str] = None
    full_address_lo: Optional[str] = None
    full_address_en: Optional[str] = None
    is_primary: Optional[bool] = None


class PatientAddressRead(PatientAddressBase, ORMBaseModel):
    patient_id: UUID
    address_type: str
    created_at: datetime
    updated_at: datetime



# =========================================================
# Patient Image
# =========================================================

class PatientImageBase(BaseModel):
    file_path: str
    image_type: Optional[str] = Field(None, description="Image type (e.g. JPEG)")
    description: Optional[str] = Field(None, description="Additional note")


class PatientImageCreate(PatientImageBase):
    patient_id: UUID


class PatientImageUpdate(BaseModel):
    file_path: Optional[str] = Field(None, description="URL file path image")
    image_type: Optional[str] = Field(None, description="Image type (e.g. JPEG)")
    description: Optional[str] = Field(None, description="Additional note")


class PatientImageRead(PatientImageBase, ORMBaseModel):
    id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime



###=====Patient-related=====###

# =========================================================
# Sources
# =========================================================

class SourceBase(BaseModel):
    source_name: str
    description: Optional[str] = None
    is_active: bool = True
    source_type: Optional[str] = None   # ✅ NEW: 'referral' | 'market' | None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    source_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    source_type: Optional[str] = None   # ✅ NEW


class SourceRead(SourceBase, ORMBaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


# =========================================================
# Alerts
# =========================================================

class AlertBase(BaseModel):
    alert_type: str
    description: str
    is_active: bool = True


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    alert_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AlertRead(AlertBase, ORMBaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


# =========================================================
# Allergies
# =========================================================

class AllergyBase(BaseModel):
    allergy_name: str
    description: Optional[str] = None
    is_active: bool = True
    allergy_type: Optional[str] = None  # 'drug', 'food', 'other' หรือ None


class AllergyCreate(AllergyBase):
    pass


class AllergyUpdate(BaseModel):
    allergy_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    allergy_type: Optional[str] = None


class AllergyRead(AllergyBase, ORMBaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime



# =========================================================
# Marketing Staff
# =========================================================

class MarketingStaffBase(BaseModel):
    marketing_name: str
    campaign: Optional[str] = None
    is_active: bool = True


class MarketingStaffCreate(MarketingStaffBase):
    pass


class MarketingStaffUpdate(BaseModel):
    marketing_name: Optional[str] = None
    campaign: Optional[str] = None
    is_active: Optional[bool] = None


class MarketingStaffRead(MarketingStaffBase, ORMBaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime




# =========================================================
# Patient Type
# =========================================================

class PatientTypeBase(BaseModel):
    type_name: str
    description: Optional[str] = None
    is_active: bool = True


class PatientTypeCreate(PatientTypeBase):
    pass


class PatientTypeUpdate(BaseModel):
    type_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PatientTypeRead(PatientTypeBase, ORMBaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


# =========================================================
# Profession
# (มีอยู่ใน DB แต่ยังไม่เคยใช้ใน service เดิมมากนัก – เตรียม schema ไว้ให้)
# =========================================================

class ProfessionBase(BaseModel):
    profession_name: str
    description: Optional[str] = None
    is_active: bool = True


class ProfessionCreate(ProfessionBase):
    pass


class ProfessionUpdate(BaseModel):
    profession_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProfessionRead(ProfessionBase, ORMBaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


# =========================================================
# Sale Staff
# =========================================================

class SaleStaffBase(BaseModel):
    sale_person_name: str
    department_name: Optional[str] = None
    is_active: bool = True


class SaleStaffCreate(SaleStaffBase):
    pass


class SaleStaffUpdate(BaseModel):
    sale_person_name: Optional[str] = None
    department_name: Optional[str] = None
    is_active: Optional[bool] = None


class SaleStaffRead(SaleStaffBase, ORMBaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

