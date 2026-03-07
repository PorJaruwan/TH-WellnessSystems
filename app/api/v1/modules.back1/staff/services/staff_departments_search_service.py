from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffDepartmentDTO
from app.api.v1.modules.staff.repositories.staff_departments_search_repository import StaffDepartmentsSearchRepository


class StaffDepartmentsSearchService:
    def __init__(self, repo: StaffDepartmentsSearchRepository):
        self.repo = repo

    async def search(
        self,
        staff_id: Optional[UUID],
        department_id: Optional[UUID],
        is_active: bool,
        limit: int,
        offset: int,
    ):
        rows, total = await self.repo.search(
            staff_id=staff_id, department_id=department_id, is_active=is_active, limit=limit, offset=offset
        )
        items = [StaffDepartmentDTO.model_validate(r) for r in rows]
        return items, total
