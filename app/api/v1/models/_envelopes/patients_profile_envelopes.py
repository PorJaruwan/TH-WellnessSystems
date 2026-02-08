# app/api/v1/models/_envelopes/patients_envelopes.py

from __future__ import annotations

from typing import Any, Dict, List, TypeAlias
from pydantic import Field

from app.api.v1.models._envelopes.base import EnvelopeBase, SuccessEnvelope, ErrorEnvelope
from app.api.v1.models.patients_model import PatientRead


class PatientSearchData(EnvelopeBase):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any] = Field(default_factory=dict)
    patients: List[PatientRead] = Field(default_factory=list)


class PatientByIdData(EnvelopeBase):
    patient: PatientRead


class PatientCreateData(EnvelopeBase):
    patient: PatientRead


class PatientUpdateData(EnvelopeBase):
    patient: PatientRead


class PatientDeleteData(EnvelopeBase):
    patient_id: str


PatientSearchEnvelope: TypeAlias = SuccessEnvelope[PatientSearchData] | ErrorEnvelope
PatientByIdEnvelope: TypeAlias = SuccessEnvelope[PatientByIdData] | ErrorEnvelope
PatientCreateEnvelope: TypeAlias = SuccessEnvelope[PatientCreateData] | ErrorEnvelope
PatientUpdateEnvelope: TypeAlias = SuccessEnvelope[PatientUpdateData] | ErrorEnvelope
PatientDeleteEnvelope: TypeAlias = SuccessEnvelope[PatientDeleteData] | ErrorEnvelope
