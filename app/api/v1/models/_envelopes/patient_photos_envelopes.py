# app/api/v1/models/_envelopes/patient_photos_envelopes.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.api.v1.models._envelopes._list_envelopes import SuccessEnvelope, Paging, Sort
from app.api.v1.models.patient_photos_models import PatientPhotoRead


class PatientPhotoFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    q: Optional[str] = None
    patient_id: Optional[UUID] = None


class PatientPhotoSingleData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item: PatientPhotoRead


class PatientPhotoSingleEnvelope(SuccessEnvelope):
    data: PatientPhotoSingleData


class PatientPhotoListData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: PatientPhotoFilters
    sort: Sort
    paging: Paging
    items: List[PatientPhotoRead]


class PatientPhotoListEnvelope(SuccessEnvelope):
    data: PatientPhotoListData


class PatientPhotoDeleteData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    photo_id: UUID


class PatientPhotoDeleteEnvelope(SuccessEnvelope):
    data: PatientPhotoDeleteData


class PatientPhotoUploadData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: UUID
    file_url: str


class PatientPhotoUploadEnvelope(SuccessEnvelope):
    data: PatientPhotoUploadData
