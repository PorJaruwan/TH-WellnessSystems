from __future__ import annotations

from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffLeaveDTO
from app.api.v1.modules.staff.repositories.staff_leave_read_repository import StaffLeaveReadRepository


class StaffLeaveReadService:
    def __init__(self, repo: StaffLeaveReadRepository):
        self.repo = repo

    async def get_by_id(self, staff_leave_id: UUID):
        obj = await self.repo.get_by_id(staff_leave_id)
        if not obj:
            return None
        return StaffLeaveDTO.model_validate(obj)
