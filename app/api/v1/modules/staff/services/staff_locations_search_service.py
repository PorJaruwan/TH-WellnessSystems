from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffLocationDTO
from app.api.v1.modules.staff.repositories.staff_locations_search_repository import StaffLocationsSearchRepository


class StaffLocationsSearchService:
    def __init__(self, repo: StaffLocationsSearchRepository):
        self.repo = repo

    async def search(
        self,
        staff_id: Optional[UUID],
        location_id: Optional[UUID],
        is_active: bool,
        limit: int,
        offset: int,
    ):
        rows, total = await self.repo.search(
            staff_id=staff_id,
            location_id=location_id,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        items = [StaffLocationDTO.model_validate(r) for r in rows]
        return items, total
