# app/api/v1/models/_envelopes/allergies_envelopes.py

from __future__ import annotations
from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patient_masterdata_model import AllergyDTO



class AllergySingleData(BaseModel):
    allergy: AllergyDTO


class AllergySingleEnvelope(SuccessEnvelope):
    data: AllergySingleData


class AllergyListData(BaseModel):
    filters: dict
    sort: Sort            # ✅ ADD
    paging: Paging
    items: List[AllergyDTO]


class AllergyListEnvelope(SuccessEnvelope):
    data: AllergyListData


class AllergyDeleteData(BaseModel):
    allergy_id: str


class AllergyDeleteEnvelope(SuccessEnvelope):
    data: AllergyDeleteData
