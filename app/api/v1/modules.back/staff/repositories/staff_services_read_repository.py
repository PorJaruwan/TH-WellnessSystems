from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import StaffService


class StaffServicesReadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, staff_service_id: UUID):
        return await self.db.get(StaffService, staff_service_id)
