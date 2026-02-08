# app/api/v1/models/patient_photos_models.py
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PatientPhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    file_path: str
    uploaded_at: datetime
