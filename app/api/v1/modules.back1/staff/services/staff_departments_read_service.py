from __future__ import annotations

from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffDepartmentDTO
from app.api.v1.modules.staff.repositories.staff_departments_read_repository import StaffDepartmentsReadRepository


class StaffDepartmentsReadService:
    def __init__(self, repo: StaffDepartmentsReadRepository):
        self.repo = repo

    async def get_by_id(self, staff_department_id: UUID):
        obj = await self.repo.get_by_id(staff_department_id)
        if not obj:
            return None
        return StaffDepartmentDTO.model_validate(obj)
