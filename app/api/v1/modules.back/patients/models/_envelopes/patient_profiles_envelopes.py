"""Patient Profiles envelopes — WellPlus Standard compliant.

Single responses -> data.item
"""
from __future__ import annotations

from pydantic import BaseModel

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope
from app.api.v1.modules.patients.models.dtos import (
    PatientProfileDTO,
    PatientContactDTO,
    PatientMedicalFlagsDTO,
    PatientMarketingDTO,
)

class PatientProfileGetData(BaseModel):
    item: PatientProfileDTO

class PatientProfileGetEnvelope(SuccessEnvelope):
    data: PatientProfileGetData

class PatientProfilePatchData(BaseModel):
    item: PatientProfileDTO

class PatientProfilePatchEnvelope(SuccessEnvelope):
    data: PatientProfilePatchData

class PatientContactGetData(BaseModel):
    item: PatientContactDTO

class PatientContactGetEnvelope(SuccessEnvelope):
    data: PatientContactGetData

class PatientContactPatchData(BaseModel):
    item: PatientContactDTO

class PatientContactPatchEnvelope(SuccessEnvelope):
    data: PatientContactPatchData

class PatientMedicalFlagsGetData(BaseModel):
    item: PatientMedicalFlagsDTO

class PatientMedicalFlagsGetEnvelope(SuccessEnvelope):
    data: PatientMedicalFlagsGetData

class PatientMedicalFlagsPatchData(BaseModel):
    item: PatientMedicalFlagsDTO

class PatientMedicalFlagsPatchEnvelope(SuccessEnvelope):
    data: PatientMedicalFlagsPatchData

class PatientMarketingGetData(BaseModel):
    item: PatientMarketingDTO

class PatientMarketingGetEnvelope(SuccessEnvelope):
    data: PatientMarketingGetData

class PatientMarketingPatchData(BaseModel):
    item: PatientMarketingDTO

class PatientMarketingPatchEnvelope(SuccessEnvelope):
    data: PatientMarketingPatchData
