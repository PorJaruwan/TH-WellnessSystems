
from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

# ✅ Reuse PatientImage table for photos (existing DB model in this project)
from app.db.models.patient_settings import PatientImage


_ALLOWED_SORT_FIELDS = {
    "created_at": PatientImage.created_at,
    "updated_at": PatientImage.updated_at,
    "patient_id": PatientImage.patient_id,
    "file_path": PatientImage.file_path,
}

DEFAULT_SORT_BY = "created_at"
DEFAULT_SORT_ORDER = "desc"


class PatientPhotosRepository:
    """DB access for patient photos (stored in PatientImage table)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        *,
        q: str = "",
        patient_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = DEFAULT_SORT_BY,
        sort_order: str = DEFAULT_SORT_ORDER,
    ) -> Tuple[List[PatientImage], int]:
        filters = []
        if patient_id:
            filters.append(PatientImage.patient_id == patient_id)
        if q:
            kw = f"%{q}%"
            filters.append(or_(func.coalesce(PatientImage.file_path, "").ilike(kw),
                              func.coalesce(PatientImage.description, "").ilike(kw)))

        total_stmt = select(func.count()).select_from(PatientImage).where(*filters)
        total = int((await self.db.execute(total_stmt)).scalar() or 0)

        col = _ALLOWED_SORT_FIELDS.get(sort_by, _ALLOWED_SORT_FIELDS[DEFAULT_SORT_BY])
        col = asc(col) if sort_order == "asc" else desc(col)

        stmt = select(PatientImage).where(*filters).order_by(col).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all()), total

    async def get_by_id(self, photo_id: UUID) -> Optional[PatientImage]:
        stmt = select(PatientImage).where(PatientImage.id == photo_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_latest_by_patient(self, patient_id: UUID) -> Optional[PatientImage]:
        stmt = (
            select(PatientImage)
            .where(PatientImage.patient_id == patient_id)
            .order_by(PatientImage.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, obj: PatientImage) -> PatientImage:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: PatientImage) -> None:
        await self.db.delete(obj)
        await self.db.commit()
