from __future__ import annotations

from uuid import UUID

from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.modules.staff.models.dtos import StaffLeaveDTO
from app.api.v1.modules.staff.models.schemas import StaffLeaveCreateModel, StaffLeaveUpdateModel
from app.api.v1.modules.staff.repositories.staff_leave_crud_repository import StaffLeaveCrudRepository


class StaffLeaveCrudService:
    def __init__(self, repo: StaffLeaveCrudRepository):
        self.repo = repo

    async def create(self, payload: StaffLeaveCreateModel):
        obj = await self.repo.create(clean_create(payload))
        return StaffLeaveDTO.model_validate(obj)

    async def update(self, staff_leave_id: UUID, payload: StaffLeaveUpdateModel):
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise ValueError("No fields to update")
        obj = await self.repo.update(staff_leave_id, clean_update(payload))
        if not obj:
            return None
        return StaffLeaveDTO.model_validate(obj)

    async def delete(self, staff_leave_id: UUID) -> bool:
        return await self.repo.delete(staff_leave_id)
