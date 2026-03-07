from __future__ import annotations

from uuid import UUID
from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.rooms_search_repository import RoomSearchRepository


class RoomSearchService(BaseSettingsSearchService):
    def __init__(self, repo: RoomSearchRepository):
        super().__init__(repo=repo)

    async def search(
        self,
        q: str = "",
        location_id: UUID | None = None,
        building_id: UUID | None = None,
        room_type_id: UUID | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        return await self.repo.search(
            q=q,
            location_id=location_id,
            building_id=building_id,
            room_type_id=room_type_id,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )