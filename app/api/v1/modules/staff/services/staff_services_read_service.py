from __future__ import annotations

from uuid import UUID

from app.api.v1.modules.staff.models.dtos import StaffServiceDTO
from app.api.v1.modules.staff.repositories.staff_services_read_repository import StaffServicesReadRepository


class StaffServicesReadService:
    def __init__(self, repo: StaffServicesReadRepository):
        self.repo = repo

    async def get_by_id(self, staff_service_id: UUID):
        obj = await self.repo.get_by_id(staff_service_id)
        if not obj:
            return None
        return StaffServiceDTO.model_validate(obj)
