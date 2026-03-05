# app/api/v1/modules/patients/services/patients_read_service.py
from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.api.v1.modules.patients.models.patients_model import PatientRead
from app.api.v1.modules.patients.repositories.patients_read_repository import PatientsReadRepository


class PatientsReadService:
    """Read service for Patient detail (GET by id).

    ✅ Service rules:
    - No FastAPI imports
    - No ResponseHandler usage
    - Return dict/DTO only
    """

    def __init__(self, repo: PatientsReadRepository):
        self.repo = repo

    async def get_by_id(self, patient_id: UUID) -> Optional[dict]:
        obj = await self.repo.get_by_id(patient_id)
        if not obj:
            return None
        return PatientRead.model_validate(obj).model_dump()
