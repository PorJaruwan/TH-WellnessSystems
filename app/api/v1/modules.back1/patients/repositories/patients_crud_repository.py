from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.patient_settings import Patient
from app.api.v1.modules.patients.models.schemas import PatientCreate, PatientUpdate
from app.api.v1.modules.patients.models.dtos import PatientRead


class PatientsCrudRepository:
    """CRUD repository for Patients (DB-only).

    ✅ Rules (WellPlus standard):
    - Repository must NOT commit/rollback.
    - Repository may flush/refresh only.
    - Transaction boundary lives in Service (commit/rollback there).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _with_refs(stmt):
        # ✅ Only load relationships that PatientRead expects.
        return stmt.options(
            selectinload(Patient.allergy),
            selectinload(Patient.drug_allergy),
            selectinload(Patient.alert),
        )

    @staticmethod
    def _raise_integrity_error(e: IntegrityError) -> None:
        msg = str(getattr(e, "orig", e)).lower()
        if "ak_patients_email" in msg:
            raise ValueError("email already exists")
        if "ak_patients_id_card_no" in msg:
            raise ValueError("id_card_no already exists")
        if "ak_patients_code" in msg:
            raise ValueError("patient_code already exists")
        raise ValueError("duplicate key / integrity error")

    @staticmethod
    def _to_read_dict(obj: Patient) -> dict:
        return PatientRead.model_validate(obj).model_dump()

    async def get_by_id(self, patient_id: UUID) -> Optional[dict]:
        stmt = self._with_refs(select(Patient)).where(Patient.id == patient_id)
        obj = (await self.db.execute(stmt)).scalars().first()
        return self._to_read_dict(obj) if obj else None

    async def create(self, payload: PatientCreate) -> dict:
        obj = Patient(**payload.model_dump(exclude_none=True))
        self.db.add(obj)
        try:
            await self.db.flush()
        except IntegrityError as e:
            self._raise_integrity_error(e)

        await self.db.refresh(obj)
        return self._to_read_dict(obj)

    async def patch(self, patient_id: UUID, payload: PatientUpdate) -> dict:
        obj = await self.db.get(Patient, patient_id)
        if not obj:
            raise ValueError("patient not found")

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise ValueError("no fields to update")

        for k, v in updates.items():
            setattr(obj, k, v)

        try:
            await self.db.flush()
        except IntegrityError as e:
            self._raise_integrity_error(e)

        await self.db.refresh(obj)
        # Re-load with refs to match read dict expectation
        found = await self.get_by_id(patient_id)
        # found cannot be None here, but keep safe
        return found or self._to_read_dict(obj)

    async def delete(self, patient_id: UUID) -> UUID:
        obj = await self.db.get(Patient, patient_id)
        if not obj:
            raise ValueError("patient not found")

        await self.db.delete(obj)
        await self.db.flush()
        return obj.id
