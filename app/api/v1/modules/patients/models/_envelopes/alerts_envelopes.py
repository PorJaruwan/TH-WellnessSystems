# app/api/v1/models/_envelopes/alerts_envelopes.py

from pydantic import BaseModel
from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.modules.patients.models.dtos import AlertDTO


class AlertListData(BaseModel):
    items: list[AlertDTO]


class AlertSingleData(BaseModel):
    filters: dict
    sort: Sort
    paging: Paging
    items: list[AlertDTO]

class AlertDeleteData(BaseModel):
    deleted: bool
    id: int


class AlertListEnvelope(SuccessEnvelope[AlertListData]):
    pass


class AlertSingleEnvelope(SuccessEnvelope[AlertSingleData]):
    pass


class AlertCreateEnvelope(SuccessEnvelope[AlertSingleData]):
    pass


class AlertUpdateEnvelope(SuccessEnvelope[AlertSingleData]):
    pass


class AlertDeleteEnvelope(SuccessEnvelope[AlertDeleteData]):
    pass