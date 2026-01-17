# app/api/v1/settings/patient_model.py
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

# # ==============================
# #Patients-old
# # ==============================
# class PatientsCreateModel(BaseModel):
#     id: UUID
#     patient_code: str = Field(None, description="unique: patient code")
#     first_name_en: Optional[str] = None
#     last_name_en: Optional[str] = None
#     first_name_lo: str
#     last_name_lo: str
#     id_card_no: str = Field(None, description="unique: id card")
#     social_security_id: Optional[str] = None
#     sex: Optional[str] = Field(None, description="check: male, female, lgbtq")
#     birth_date: Optional[datetime] = None
#     religion: Optional[str] = None
#     department_type_id: Optional[str] = Field(None, description="foreign key: department_type-id")
#     profession_id: Optional[str] = Field(None, description="foreign key: professions-id")
#     patient_type_id: Optional[str] = Field(None, description="foreign key: patients_type-id")
#     telephone: Optional[str] = None
#     work_phone: Optional[str] = None
#     email: str = Field(None, description="unique: email")
#     line_id: Optional[str] = None
#     facebook: Optional[str] = None
#     whatsapp: Optional[str] = None
#     payment_status: str
#     allergy_id: Optional[str] = Field(None, description="foreign key: allergies-id")
#     allergy_note: Optional[str] = None
#     contact_first_name: Optional[str] = None
#     contact_last_name: Optional[str] = None
#     contact_phone1: Optional[str] = None
#     contact_phone2: Optional[str] = None
#     relationship: Optional[str] = None
#     alert_id: Optional[str] = Field(None, description="foreign key: alerts-id")
#     marketing_person_id: Optional[str] = Field(None, description="foreign key: marketings-id")
#     customer_profile_id: Optional[str] = Field(None, description="foreign key: customer_profiles-id")
#     locations_id: Optional[str] = Field(None, description="foreign key: locations-id")
#     source_id: Optional[str] = Field(None, description="foreign key: sources-id")
#     status: Optional[str] = None
#     is_active: bool
#     patient_note: Optional[str] = None
#     created_at: datetime
#     updated_at: datetime
#     title_lo: Optional[str] = None
#     title_en: Optional[str] = None
#     title_cc: Optional[str] = None
#     alert_note: Optional[str] = None
#     full_name_lo: str #first_name_lo + last_name_lo
#     full_name_en: Optional[str] = None #first_name_en + last_name_en
#     main_contact_method: Optional[str] = None
#     drug_allergy_id: Optional[str] = Field(None, description="foreign key: allergies-id")

# class PatientsUpdateModel(BaseModel):
#     first_name_en: str
#     last_name_en: str
#     first_name_lo: str
#     last_name_lo: str
#     id_card_no: str
#     social_security_id: str
#     sex: str
#     birth_date: datetime
#     religion: Optional[str]
#     profession_id: Optional[str]
#     patient_type_id: Optional[str]
#     telephone: str
#     work_phone: str
#     email: str
#     line_id: str
#     facebook: str
#     whatsapp: str
#     payment_status: str
#     allergy_id: Optional[str]
#     allergy_note: str
#     contact_first_name: str
#     contact_last_name: str
#     contact_phone1: str
#     contact_phone2: str
#     relationship: Optional[str]
#     alert_id: Optional[str]
#     #salesstaff_id: Optional[str]
#     marketing_person_id: Optional[str]
#     customer_profile_id: Optional[str]
#     locations_id: Optional[str]
#     source_id: Optional[str]
#     status: str
#     is_active: bool
#     patient_note: str
#     updated_at: datetime
#     title_lo: str
#     title_en: str
#     title_cc: str
#     alert_note: str
#     full_name_lo: str
#     full_name_en: str
#     main_contact_method: str
#     drug_allergy_id: str



# ==============================
#sources
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
#alerts
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
#Allergies
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
#Marketing Staff
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
#Patient Addresses
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
#Patient Image
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
#Patient Type
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
#Sale Staff
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