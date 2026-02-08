# app/api/v1/models/patient_profiles_model.py

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date


# =========================================================
# DTOs (Search models) - from ORM Patient
# =========================================================
class PatientSearchItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_code: str
    full_name_lo: str
    telephone: Optional[str] = None
    status: str
    is_active: bool = True


# =========================================================
# DTOs (Read models) - from ORM Patient
# =========================================================

class PatientProfileDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_code: str

    title_lo: Optional[str] = None
    first_name_lo: str
    last_name_lo: str
    title_en: Optional[str] = None
    first_name_en: Optional[str] = None
    last_name_en: Optional[str] = None

    sex: Optional[str] = None
    birth_date: Optional[date] = None
    id_card_no: str

    patient_type_id: Optional[UUID] = None
    profession_id: Optional[UUID] = None

    status: str
    is_active: bool = True

    full_name_lo: str
    full_name_en: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class PatientContactDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    email: Optional[str] = None
    telephone: Optional[str] = None
    work_phone: Optional[str] = None

    line_id: Optional[str] = None
    facebook: Optional[str] = None
    whatsapp: Optional[str] = None

    main_contact_method: Optional[str] = None

    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    contact_phone1: Optional[str] = None
    contact_phone2: Optional[str] = None
    contact_relationship: Optional[str] = None


class PatientMedicalFlagsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    allergy_id: Optional[UUID] = None
    drug_allergy_id: Optional[UUID] = None
    allergy_note: Optional[str] = None

    alert_id: Optional[UUID] = None
    alert_note: Optional[str] = None
    alert_level: Optional[str] = None

    critical_medical_note: Optional[str] = None


class PatientMarketingDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    source_id: Optional[UUID] = None
    market_source_id: Optional[UUID] = None

    referral_source_note: Optional[str] = Field(None, max_length=500)
    market_source_note: Optional[str] = Field(None, max_length=500)

    salesperson_id: Optional[UUID] = None
    marketing_person_id: Optional[UUID] = None


# class PatientSearchItemDTO(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     id: UUID
#     patient_code: str
#     full_name_lo: str
#     telephone: Optional[str] = None
#     status: str
#     is_active: bool = True


# =========================================================
# Patch payloads (sub-resource)
# =========================================================

class PatientProfilePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_code: Optional[str] = None

    title_lo: Optional[str] = None
    first_name_lo: Optional[str] = None
    last_name_lo: Optional[str] = None

    title_en: Optional[str] = None
    first_name_en: Optional[str] = None
    last_name_en: Optional[str] = None

    sex: Optional[str] = None
    birth_date: Optional[date] = None
    id_card_no: Optional[str] = None

    patient_type_id: Optional[UUID] = None
    profession_id: Optional[UUID] = None

    status: Optional[str] = None
    is_active: Optional[bool] = None


class PatientContactPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Optional[str] = None
    telephone: Optional[str] = None
    work_phone: Optional[str] = None

    line_id: Optional[str] = None
    facebook: Optional[str] = None
    whatsapp: Optional[str] = None

    main_contact_method: Optional[str] = None

    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    contact_phone1: Optional[str] = None
    contact_phone2: Optional[str] = None
    contact_relationship: Optional[str] = None


class PatientMedicalFlagsPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allergy_id: Optional[UUID] = None
    drug_allergy_id: Optional[UUID] = None
    allergy_note: Optional[str] = None

    alert_id: Optional[UUID] = None
    alert_note: Optional[str] = None
    alert_level: Optional[str] = None

    critical_medical_note: Optional[str] = None


class PatientMarketingPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: Optional[UUID] = None
    market_source_id: Optional[UUID] = None

    referral_source_note: Optional[str] = None
    market_source_note: Optional[str] = None

    salesperson_id: Optional[UUID] = None
    marketing_person_id: Optional[UUID] = None


# =========================================================
# List wrapper standard (filters + paging + items)
# =========================================================

class Paging(BaseModel):
    total: int
    limit: int
    offset: int


class ListStandard(BaseModel):
    filters: Dict[str, Any]
    paging: Paging
    items: List[Any]
