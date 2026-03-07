from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.patients.models.patients_model import PatientCreate, PatientUpdate
from app.api.v1.modules.patients.repositories.patients_crud_repository import PatientsCrudRepository


class PatientsCrudService:
    """Business layer for Patients CRUD (transaction boundary)."""

    def __init__(self, db: AsyncSession, repo: PatientsCrudRepository):
        self.db = db
        self.repo = repo

    async def create(self, payload: PatientCreate) -> dict:
        try:
            created = await self.repo.create(payload)
            await self.db.commit()
            return created
        except Exception:
            await self.db.rollback()
            raise

    async def get_by_id(self, patient_id: UUID) -> dict | None:
        return await self.repo.get_by_id(patient_id)

    async def patch(self, patient_id: UUID, payload: PatientUpdate) -> dict:
        try:
            updated = await self.repo.patch(patient_id, payload)
            await self.db.commit()
            return updated
        except Exception:
            await self.db.rollback()
            raise

    async def delete(self, patient_id: UUID) -> UUID:
        try:
            deleted_id = await self.repo.delete(patient_id)
            await self.db.commit()
            return deleted_id
        except Exception:
            await self.db.rollback()
            raise
