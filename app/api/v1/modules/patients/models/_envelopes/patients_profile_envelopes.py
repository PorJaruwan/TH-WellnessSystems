"""Patients envelopes (read + basic CRUD legacy)

WellPlus Standard:
- List/Search -> data.items
- Single      -> data.item
"""
from __future__ import annotations

from pydantic import BaseModel
from typing import Optional

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope
from app.api.v1.modules.patients.models.dtos import PatientRead


class PatientByIdData(BaseModel):
    item: PatientRead


class PatientByIdEnvelope(SuccessEnvelope):
    data: PatientByIdData


class PatientCreateData(BaseModel):
    item: PatientRead


class PatientCreateEnvelope(SuccessEnvelope):
    data: PatientCreateData


class PatientUpdateData(BaseModel):
    item: PatientRead


class PatientUpdateEnvelope(SuccessEnvelope):
    data: PatientUpdateData


class PatientDeleteData(BaseModel):
    item: dict  # {"patient_id": "..."} or similar


class PatientDeleteEnvelope(SuccessEnvelope):
    data: PatientDeleteData
