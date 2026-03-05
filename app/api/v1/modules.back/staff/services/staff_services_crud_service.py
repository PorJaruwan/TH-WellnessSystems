from __future__ import annotations

from uuid import UUID

from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.modules.staff.models.dtos import StaffServiceDTO
from app.api.v1.modules.staff.models.schemas import StaffServicesCreateModel, StaffServicesUpdateModel
from app.api.v1.modules.staff.repositories.staff_services_crud_repository import StaffServicesCrudRepository


class StaffServicesCrudService:
    def __init__(self, repo: StaffServicesCrudRepository):
        self.repo = repo

    async def create(self, payload: StaffServicesCreateModel):
        obj = await self.repo.create(clean_create(payload))
        return StaffServiceDTO.model_validate(obj)

    async def update(self, staff_service_id: UUID, payload: StaffServicesUpdateModel):
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise ValueError("No fields to update")
        obj = await self.repo.update(staff_service_id, clean_update(payload))
        if not obj:
            return None
        return StaffServiceDTO.model_validate(obj)

    async def delete(self, staff_service_id: UUID) -> bool:
        return await self.repo.delete(staff_service_id)
