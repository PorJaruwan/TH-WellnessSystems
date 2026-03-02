"""V2 envelopes for Patients CRUD (create/update/delete) — WellPlus Standard compliant.

- Single responses must return: data.item
"""
from __future__ import annotations

from pydantic import BaseModel

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope
from app.api.v1.modules.patients.models.dtos import PatientRead


class PatientCrudSingleData(BaseModel):
    item: PatientRead


class PatientCreateEnvelopeV2(SuccessEnvelope):
    data: PatientCrudSingleData


class PatientUpdateEnvelopeV2(SuccessEnvelope):
    data: PatientCrudSingleData


class PatientDeleteData(BaseModel):
    item: dict  # {"patient_id": "..."} or similar


class PatientDeleteEnvelopeV2(SuccessEnvelope):
    data: PatientDeleteData
