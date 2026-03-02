from __future__ import annotations

from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.modules.patients.models.patient_masterdata_model import SourceDTO


class SourceSingleData(BaseModel):
    item: SourceDTO


class SourceSingleEnvelope(SuccessEnvelope):
    data: SourceSingleData


class SourceListData(BaseModel):
    filters: dict
    sort: Sort
    paging: Paging
    items: List[SourceDTO]


class SourceListEnvelope(SuccessEnvelope):
    data: SourceListData


class SourceDeleteData(BaseModel):
    source_id: str


class SourceDeleteEnvelope(SuccessEnvelope):
    data: SourceDeleteData