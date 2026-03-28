from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.modules.staff.models.dtos import StaffDepartmentDTO
from app.api.v1.modules.staff.models.schemas import StaffDepartmentsCreateModel, StaffDepartmentsUpdateModel
from app.api.v1.modules.staff.repositories.staff_departments_crud_repository import StaffDepartmentsCrudRepository


class StaffDepartmentsCrudService:
    def __init__(self, db: AsyncSession, repo: StaffDepartmentsCrudRepository):
        self.db = db
        self.repo = repo

    async def create(self, payload: StaffDepartmentsCreateModel):
        try:
            obj = await self.repo.create(clean_create(payload))
            await self.db.commit()
            return StaffDepartmentDTO.model_validate(obj)
        except Exception:
            await self.db.rollback()
            raise

    async def update(self, staff_department_id: UUID, payload: StaffDepartmentsUpdateModel):
        try:
            updates = payload.model_dump(exclude_unset=True)
            if not updates:
                raise ValueError("No fields to update")

            obj = await self.repo.update(staff_department_id, clean_update(payload))
            if not obj:
                return None

            await self.db.commit()
            return StaffDepartmentDTO.model_validate(obj)
        except Exception:
            await self.db.rollback()
            raise

    async def delete(self, staff_department_id: UUID) -> bool:
        try:
            ok = await self.repo.delete(staff_department_id)
            if not ok:
                return False

            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            raise
