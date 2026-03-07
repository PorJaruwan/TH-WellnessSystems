from __future__ import annotations

from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.modules.patients.models.dtos import PatientTypeDTO


class PatientTypeSingleData(BaseModel):
    item: PatientTypeDTO


class PatientTypeSingleEnvelope(SuccessEnvelope):
    data: PatientTypeSingleData


class PatientTypeListData(BaseModel):
    filters: dict
    sort: Sort
    paging: Paging
    items: List[PatientTypeDTO]


class PatientTypeListEnvelope(SuccessEnvelope):
    data: PatientTypeListData


class PatientTypeDeleteData(BaseModel):
    deleted: bool
    id: str


class PatientTypeDeleteEnvelope(SuccessEnvelope):
    data: PatientTypeDeleteData