from __future__ import annotations

from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffLocationDTO
from app.api.v1.modules.staff.repositories.staff_locations_read_repository import StaffLocationsReadRepository


class StaffLocationsReadService:
    def __init__(self, repo: StaffLocationsReadRepository):
        self.repo = repo

    async def get_by_id(self, staff_location_id: UUID):
        obj = await self.repo.get_by_id(staff_location_id)
        return StaffLocationDTO.model_validate(obj) if obj else None
