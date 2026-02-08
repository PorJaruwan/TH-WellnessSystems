# app/api/v1/models/_envelopes/patient_addresses_envelopes.py

from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patients_model import PatientAddressRead


class PatientAddressFilters(BaseModel):
    q: Optional[str] = None
    patient_id: Optional[str] = None
    address_type: Optional[str] = None
    is_primary: Optional[bool] = None


class PatientAddressSingleData(BaseModel):
    item: PatientAddressRead


class PatientAddressSingleEnvelope(SuccessEnvelope):
    data: PatientAddressSingleData


class PatientAddressListData(BaseModel):
    filters: PatientAddressFilters
    sort: Sort
    paging: Paging
    items: List[PatientAddressRead]


class PatientAddressListEnvelope(SuccessEnvelope):
    data: PatientAddressListData


class PatientAddressDeleteData(BaseModel):
    patient_id: str
    address_type: str


class PatientAddressDeleteEnvelope(SuccessEnvelope):
    data: PatientAddressDeleteData
