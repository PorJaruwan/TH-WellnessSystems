from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import StaffLocation


class StaffLocationsReadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, staff_location_id: UUID):
        stmt = select(StaffLocation).where(StaffLocation.id == staff_location_id)
        return (await self.db.execute(stmt)).scalars().first()
