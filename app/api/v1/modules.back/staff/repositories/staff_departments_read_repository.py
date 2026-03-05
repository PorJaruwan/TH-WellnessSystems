from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import StaffDepartment


class StaffDepartmentsReadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, staff_department_id: UUID):
        return await self.db.get(StaffDepartment, staff_department_id)
