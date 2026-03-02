# app/api/v1/modules/patients/repositories/patients_read_repository.py
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.patient_settings import Patient


class PatientsReadRepository:
    """Read-only repository for Patient detail endpoints.

    ✅ Design rule:
    - Read endpoints may load ORM object(s)
    - But should be explicit about eager loads (avoid accidental lazy-load)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        res = await self.db.execute(select(Patient).where(Patient.id == patient_id))
        return res.scalars().first()
