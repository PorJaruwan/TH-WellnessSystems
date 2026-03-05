# app/api/v1/modules/patients/repositories/patient_addresses_repository.py

from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.patient_settings import PatientAddress


ALLOWED_SORT_FIELDS = {
    "created_at": PatientAddress.created_at,
    "updated_at": PatientAddress.updated_at,
    "address_type": PatientAddress.address_type,
    "patient_id": PatientAddress.patient_id,
    "sub_district": PatientAddress.sub_district,
    "city": PatientAddress.city,
    "state_province": PatientAddress.state_province,
    "postal_code": PatientAddress.postal_code,
    "country_code": PatientAddress.country_code,
    "is_primary": PatientAddress.is_primary,
}

DEFAULT_SORT_BY = "created_at"
DEFAULT_SORT_ORDER = "desc"


class PatientAddressesRepository:
    """DB access for patient addresses."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        *,
        q: str = "",
        patient_id: Optional[UUID] = None,
        address_type: Optional[str] = None,
        is_primary: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = DEFAULT_SORT_BY,
        sort_order: str = DEFAULT_SORT_ORDER,
    ) -> Tuple[List[PatientAddress], int]:
        filters = []
        if patient_id:
            filters.append(PatientAddress.patient_id == patient_id)

        if address_type:
            filters.append(PatientAddress.address_type == address_type)

        if is_primary is not None:
            filters.append(PatientAddress.is_primary == is_primary)

        if q:
            kw = f"%{q}%"
            filters.append(
                or_(
                    func.coalesce(PatientAddress.address_line1, "").ilike(kw),
                    func.coalesce(PatientAddress.address_line2, "").ilike(kw),
                    func.coalesce(PatientAddress.sub_district, "").ilike(kw),
                    func.coalesce(PatientAddress.city, "").ilike(kw),
                    func.coalesce(PatientAddress.state_province, "").ilike(kw),
                    func.coalesce(PatientAddress.postal_code, "").ilike(kw),
                    func.coalesce(PatientAddress.address_type, "").ilike(kw),
                )
            )

        total_stmt = select(func.count()).select_from(PatientAddress).where(*filters)
        total = int((await self.db.execute(total_stmt)).scalar() or 0)

        col = ALLOWED_SORT_FIELDS.get(sort_by, ALLOWED_SORT_FIELDS[DEFAULT_SORT_BY])
        col = asc(col) if sort_order == "asc" else desc(col)

        stmt = (
            select(PatientAddress)
            .where(*filters)
            .order_by(col)
            .limit(limit)
            .offset(offset)
        )
        res = await self.db.execute(stmt)
        items = list(res.scalars().all())
        return items, total

    async def get_by_id(self, address_id: UUID) -> Optional[PatientAddress]:
        stmt = select(PatientAddress).where(PatientAddress.id == address_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_key(self, *, patient_id: UUID, address_type: str) -> Optional[PatientAddress]:
        stmt = select(PatientAddress).where(
            PatientAddress.patient_id == patient_id,
            PatientAddress.address_type == address_type,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, obj: PatientAddress) -> PatientAddress:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: PatientAddress) -> PatientAddress:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: PatientAddress) -> None:
        await self.db.delete(obj)
        await self.db.commit()