from __future__ import annotations

from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffDetailDTO
from app.api.v1.modules.staff.repositories.staff_read_repository import StaffReadRepository


class StaffReadService:
    """Business layer: read (full)."""

    def __init__(self, repo: StaffReadRepository):
        self.repo = repo

    async def get_by_id(self, staff_id: UUID) -> StaffDetailDTO | None:
        obj = await self.repo.get_by_id(staff_id)
        return StaffDetailDTO.model_validate(obj) if obj else None
