# app/api/v1/models/_envelopes/sale_staff_envelopes.py

from __future__ import annotations

from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.modules.patients.models.dtos import SaleStaffDTO


class SaleStaffSingleData(BaseModel):
    item: SaleStaffDTO


class SaleStaffSingleEnvelope(SuccessEnvelope):
    data: SaleStaffSingleData


class SaleStaffListData(BaseModel):
    filters: dict
    sort: Sort
    paging: Paging
    items: List[SaleStaffDTO]


class SaleStaffListEnvelope(SuccessEnvelope):
    data: SaleStaffListData


class SaleStaffDeleteData(BaseModel):
    deleted: bool
    id: str


class SaleStaffDeleteEnvelope(SuccessEnvelope):
    data: SaleStaffDeleteData