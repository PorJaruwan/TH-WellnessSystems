from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.staff.models.dtos import StaffDetailDTO
from app.api.v1.modules.staff.repositories.staff_crud_repository import StaffCrudRepository


class StaffCrudService:
    """Business layer: create/update/delete (transaction boundary)."""

    def __init__(self, db: AsyncSession, repo: StaffCrudRepository):
        self.db = db
        self.repo = repo

    async def create(self, payload_model) -> StaffDetailDTO:
        try:
            obj = await self.repo.create(payload_model)
            await self.db.commit()
            return StaffDetailDTO.model_validate(obj)
        except Exception:
            await self.db.rollback()
            raise

    async def update(self, staff_id: UUID, payload_model) -> StaffDetailDTO | None:
        try:
            updates = payload_model.model_dump(exclude_unset=True)
            if not updates:
                raise ValueError("No fields to update")

            obj = await self.repo.update(staff_id, payload_model)
            if not obj:
                return None

            await self.db.commit()
            return StaffDetailDTO.model_validate(obj)
        except Exception:
            await self.db.rollback()
            raise

    async def delete(self, staff_id: UUID) -> UUID:
        try:
            deleted_id = await self.repo.delete(staff_id)
            await self.db.commit()
            return deleted_id
        except Exception:
            await self.db.rollback()
            raise
        

