# app/api/v1/models/_envelopes/sources_envelopes.py

from __future__ import annotations
from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patient_masterdata_model import SourceDTO


class SourceSingleData(BaseModel):
    source: SourceDTO


class SourceSingleEnvelope(SuccessEnvelope):
    data: SourceSingleData


class SourceListData(BaseModel):
    filters: dict
    sort: Sort            # ✅ ADD
    paging: Paging
    items: List[SourceDTO]


class SourceListEnvelope(SuccessEnvelope):
    data: SourceListData


class SourceDeleteData(BaseModel):
    source_id: str


class SourceDeleteEnvelope(SuccessEnvelope):
    data: SourceDeleteData
