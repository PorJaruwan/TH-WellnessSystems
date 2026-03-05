from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import StaffLocation


class StaffLocationsCrudRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> StaffLocation:
        obj = StaffLocation(**payload)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, staff_location_id: UUID, payload: dict):
        stmt = (
            update(StaffLocation)
            .where(StaffLocation.id == staff_location_id)
            .values(**payload)
            .returning(StaffLocation)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        row = res.fetchone()
        return row[0] if row else None

    async def delete(self, staff_location_id: UUID) -> bool:
        stmt = delete(StaffLocation).where(StaffLocation.id == staff_location_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0
