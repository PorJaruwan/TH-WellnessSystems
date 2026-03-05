from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffServiceDTO
from app.api.v1.modules.staff.repositories.staff_services_search_repository import StaffServicesSearchRepository


class StaffServicesSearchService:
    def __init__(self, repo: StaffServicesSearchRepository):
        self.repo = repo

    async def search(
        self,
        staff_id: Optional[UUID],
        service_id: Optional[UUID],
        is_active: bool,
        limit: int,
        offset: int,
    ):
        rows, total = await self.repo.search(
            staff_id=staff_id, service_id=service_id, is_active=is_active, limit=limit, offset=offset
        )
        items = [StaffServiceDTO.model_validate(r) for r in rows]
        return items, total
