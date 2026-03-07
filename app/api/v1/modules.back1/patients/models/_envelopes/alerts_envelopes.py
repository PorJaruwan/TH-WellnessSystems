from __future__ import annotations

from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.modules.patients.models.dtos import AlertDTO


class AlertSingleData(BaseModel):
    item: AlertDTO


class AlertSingleEnvelope(SuccessEnvelope):
    data: AlertSingleData


class AlertListData(BaseModel):
    filters: dict
    sort: Sort
    paging: Paging
    items: List[AlertDTO]


class AlertListEnvelope(SuccessEnvelope):
    data: AlertListData


class AlertDeleteData(BaseModel):
    deleted: bool
    id: str


class AlertDeleteEnvelope(SuccessEnvelope):
    data: AlertDeleteData