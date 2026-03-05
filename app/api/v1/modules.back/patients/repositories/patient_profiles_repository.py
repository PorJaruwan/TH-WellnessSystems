
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.patient_settings import Patient


class PatientProfilesRepository:
    """DB access for patient profile fields stored on Patient table."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_patient(self, patient_id: UUID) -> Optional[Patient]:
        stmt = select(Patient).where(Patient.id == patient_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def save(self, patient: Patient) -> Patient:
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient
