from __future__ import annotations

from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.modules.patients.models.dtos import AllergyDTO


class AllergySingleData(BaseModel):
    item: AllergyDTO


class AllergySingleEnvelope(SuccessEnvelope):
    data: AllergySingleData


class AllergyListData(BaseModel):
    filters: dict
    sort: Sort
    paging: Paging
    items: List[AllergyDTO]


class AllergyListEnvelope(SuccessEnvelope):
    data: AllergyListData


class AllergyDeleteData(BaseModel):
    deleted: bool
    id: str


class AllergyDeleteEnvelope(SuccessEnvelope):
    data: AllergyDeleteData