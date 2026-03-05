from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffLeaveDTO
from app.api.v1.modules.staff.repositories.staff_leave_search_repository import StaffLeaveSearchRepository


class StaffLeaveSearchService:
    def __init__(self, repo: StaffLeaveSearchRepository):
        self.repo = repo

    async def search(
        self,
        company_code: Optional[str],
        location_id: Optional[UUID],
        staff_id: Optional[UUID],
        status: Optional[str],
        date_from: Optional[date],
        date_to: Optional[date],
        is_active: bool,
        limit: int,
        offset: int,
    ):
        rows, total = await self.repo.search(
            company_code=company_code,
            location_id=location_id,
            staff_id=staff_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        items = [StaffLeaveDTO.model_validate(r) for r in rows]
        return items, total
