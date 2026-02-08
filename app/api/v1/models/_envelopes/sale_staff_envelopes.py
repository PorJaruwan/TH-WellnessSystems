# app/api/v1/models/_envelopes/sale_staff_envelopes.py

from __future__ import annotations
from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patient_masterdata_model import SaleStaffDTO


class SaleStaffSingleData(BaseModel):
    item: SaleStaffDTO


class SaleStaffSingleEnvelope(SuccessEnvelope):
    data: SaleStaffSingleData


class SaleStaffListData(BaseModel):
    filters: dict
    sort: Sort            # ✅ ADD
    paging: Paging
    items: List[SaleStaffDTO]


class SaleStaffListEnvelope(SuccessEnvelope):
    data: SaleStaffListData


class SaleStaffDeleteData(BaseModel):
    id: str


class SaleStaffDeleteEnvelope(SuccessEnvelope):
    data: SaleStaffDeleteData
