from __future__ import annotations

from typing import Optional

from app.api.v1.modules.staff.models.dtos import StaffSearchItemDTO
from app.api.v1.modules.staff.repositories.staff_search_repository import StaffSearchRepository


class StaffSearchService:
    """Business layer: search/list."""

    def __init__(self, repo: StaffSearchRepository):
        self.repo = repo

    async def search(
        self,
        q: str = "",
        role: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[StaffSearchItemDTO], int]:
        items, total = await self.repo.search(q=q, role=role, is_active=is_active, limit=limit, offset=offset)
        dto_items = [StaffSearchItemDTO.model_validate(x) for x in items]
        return dto_items, total
