# app/api/v1/models/_envelopes/patient_types_envelopes.py

from __future__ import annotations
from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patient_masterdata_model import PatientTypeDTO


class PatientTypeSingleData(BaseModel):
    item: PatientTypeDTO


class PatientTypeSingleEnvelope(SuccessEnvelope):
    data: PatientTypeSingleData


class PatientTypeListData(BaseModel):
    filters: dict
    sort: Sort            # ✅ ADD
    paging: Paging
    items: List[PatientTypeDTO]


class PatientTypeListEnvelope(SuccessEnvelope):
    data: PatientTypeListData


class PatientTypeDeleteData(BaseModel):
    id: str


class PatientTypeDeleteEnvelope(SuccessEnvelope):
    data: PatientTypeDeleteData
