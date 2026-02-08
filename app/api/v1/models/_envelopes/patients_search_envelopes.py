# app/api/v1/models/_envelopes/patients_search_envelopes.py

from __future__ import annotations
from pydantic import BaseModel
from typing import List

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patient_profiles_model import PatientSearchItemDTO


class PatientsSearchListData(BaseModel):
    filters: dict
    sort: Sort
    paging: Paging
    items: List[PatientSearchItemDTO]


class PatientsSearchListEnvelope(SuccessEnvelope):
    data: PatientsSearchListData
