from __future__ import annotations

from uuid import UUID

from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.modules.staff.models.dtos import StaffLocationDTO
from app.api.v1.modules.staff.models.schemas import StaffLocationsCreateModel, StaffLocationsUpdateModel
from app.api.v1.modules.staff.repositories.staff_locations_crud_repository import StaffLocationsCrudRepository


class StaffLocationsCrudService:
    def __init__(self, repo: StaffLocationsCrudRepository):
        self.repo = repo

    async def create(self, payload: StaffLocationsCreateModel):
        obj = await self.repo.create(clean_create(payload))
        return StaffLocationDTO.model_validate(obj)

    async def update(self, staff_location_id: UUID, payload: StaffLocationsUpdateModel):
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise ValueError("No fields to update")
        obj = await self.repo.update(staff_location_id, clean_update(payload))
        if not obj:
            return None
        return StaffLocationDTO.model_validate(obj)

    async def delete(self, staff_location_id: UUID) -> bool:
        return await self.repo.delete(staff_location_id)
