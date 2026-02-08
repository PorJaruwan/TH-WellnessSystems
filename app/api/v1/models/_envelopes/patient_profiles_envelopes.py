# app/api/v1/models/_envelopes/patient_envelopes.py

from __future__ import annotations

from pydantic import BaseModel
from typing import Optional

from app.api.v1.models.patient_profiles_model import (
    PatientProfileDTO,
    PatientContactDTO,
    PatientMedicalFlagsDTO,
    PatientMarketingDTO,
    PatientSearchItemDTO,
    ListStandard,
)


# =========================================================
# Base Envelope (match ResponseHandler.success shape)
# =========================================================

class SuccessEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: dict


# =========================================================
# Profile
# =========================================================

class PatientProfileGetData(BaseModel):
    profile: PatientProfileDTO


class PatientProfileGetEnvelope(SuccessEnvelope):
    data: PatientProfileGetData


class PatientProfilePatchEnvelope(SuccessEnvelope):
    data: PatientProfileGetData


# =========================================================
# Contact
# =========================================================

class PatientContactGetData(BaseModel):
    contact: PatientContactDTO


class PatientContactGetEnvelope(SuccessEnvelope):
    data: PatientContactGetData


class PatientContactPatchEnvelope(SuccessEnvelope):
    data: PatientContactGetData


# =========================================================
# Medical flags
# =========================================================

class PatientMedicalFlagsGetData(BaseModel):
    medical_flags: PatientMedicalFlagsDTO


class PatientMedicalFlagsGetEnvelope(SuccessEnvelope):
    data: PatientMedicalFlagsGetData


class PatientMedicalFlagsPatchEnvelope(SuccessEnvelope):
    data: PatientMedicalFlagsGetData


# =========================================================
# Marketing
# =========================================================

class PatientMarketingGetData(BaseModel):
    marketing: PatientMarketingDTO


class PatientMarketingGetEnvelope(SuccessEnvelope):
    data: PatientMarketingGetData


class PatientMarketingPatchEnvelope(SuccessEnvelope):
    data: PatientMarketingGetData


# =========================================================
# Search (list standard)
# =========================================================

class PatientSearchListData(ListStandard):
    items: list[PatientSearchItemDTO]


class PatientSearchEnvelope(SuccessEnvelope):
    data: PatientSearchListData
