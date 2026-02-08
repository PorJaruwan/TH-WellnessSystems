# app/api/v1/models/_envelopes/marketing_staff_envelopes_v2.py

from __future__ import annotations
from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patient_masterdata_model import MarketingStaffDTO



class MarketingStaffSingleData(BaseModel):
    item: MarketingStaffDTO


class MarketingStaffSingleEnvelope(SuccessEnvelope):
    data: MarketingStaffSingleData


class MarketingStaffListData(BaseModel):
    filters: dict
    sort: Sort            # ✅ ADD
    paging: Paging
    items: List[MarketingStaffDTO]


class MarketingStaffListEnvelope(SuccessEnvelope):
    data: MarketingStaffListData


class MarketingStaffDeleteData(BaseModel):
    id: str


class MarketingStaffDeleteEnvelope(SuccessEnvelope):
    data: MarketingStaffDeleteData
