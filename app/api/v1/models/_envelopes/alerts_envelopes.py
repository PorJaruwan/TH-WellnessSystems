# app/api/v1/models/_envelopes/alerts_envelopes.py

from __future__ import annotations
from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patient_masterdata_model import AlertDTO


class AlertSingleData(BaseModel):
    alert: AlertDTO


class AlertSingleEnvelope(SuccessEnvelope): 
    data: AlertSingleData


class AlertListData(BaseModel):
    filters: dict
    sort: Sort            # ✅ ADD
    paging: Paging
    items: List[AlertDTO]


class AlertListEnvelope(SuccessEnvelope):
    data: AlertListData


class AlertDeleteData(BaseModel):
    alert_id: str


class AlertDeleteEnvelope(SuccessEnvelope):
    data: AlertDeleteData

