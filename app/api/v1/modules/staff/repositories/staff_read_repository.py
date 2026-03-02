from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Staff


class StaffReadRepository:
    """DB layer: read-by-id (full). Add eager loads here if needed."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, staff_id: UUID) -> Staff | None:
        return await self.db.get(Staff, staff_id)
