# app/api/v1/models/_envelopes/patient_images_envelopes.py
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.api.v1.models.patients_model import PatientImageRead


class PatientImageListFilters(BaseModel):
    """
    q: ค้นหาแบบ contains (DB) บน file_path/description/image_type
    patient_id: filter เฉพาะคนไข้
    image_type: filter เฉพาะประเภทภาพ
    """
    model_config = ConfigDict(extra="forbid")

    q: Optional[str] = None
    patient_id: Optional[UUID] = None
    image_type: Optional[str] = None


class Paging(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class PatientImageListData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: PatientImageListFilters
    paging: Paging
    items: List[PatientImageRead]


class PatientImageListEnvelope(BaseModel):
    """
    strict envelope for list v2
    """
    model_config = ConfigDict(extra="forbid")

    status: Literal["success", "error"]
    status_code: int
    message: str
    data: PatientImageListData


class PatientImageByIdData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_image: PatientImageRead


class PatientImageByIdEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["success", "error"]
    status_code: int
    message: str
    data: PatientImageByIdData


class PatientImageCreateEnvelope(PatientImageByIdEnvelope):
    pass


class PatientImageUpdateEnvelope(PatientImageByIdEnvelope):
    pass


class PatientImageDeleteData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_id: UUID


class PatientImageDeleteEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["success", "error"]
    status_code: int
    message: str
    data: PatientImageDeleteData
