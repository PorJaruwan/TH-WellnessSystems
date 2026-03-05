from __future__ import annotations


class RoomServiceSearchService:
    """
    Clean service (no inheritance from BaseSettingsSearchService)
    Prevents returning ORM objects that trigger lazy load.
    """

    def __init__(self, repo):
        self.repo = repo

    async def search(self, q: str, limit: int, offset: int):
        rows = await self.repo.search(q=q, limit=limit, offset=offset)

        # ถ้ายังไม่มี count query
        total = len(rows)

        return rows, total
    

# from __future__ import annotations

# from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
# from app.api.v1.modules.masters.repositories.room_services_search_repository import RoomServiceSearchRepository


# class RoomServiceSearchService(BaseSettingsSearchService):
#     def __init__(self, repo: RoomServiceSearchRepository):
#         super().__init__(repo=repo)
