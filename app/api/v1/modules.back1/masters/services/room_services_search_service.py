from __future__ import annotations

from uuid import UUID

class RoomServiceSearchService:
    """
    Clean service (no inheritance from BaseSettingsSearchService)
    Prevents returning ORM objects that trigger lazy load.
    """

    def __init__(self, repo):
        self.repo = repo

    async def search(
        self,
        q: str = "",
        room_id: UUID | None = None,
        service_id: UUID | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        rows = await self.repo.search(
            q=q,
            room_id=room_id,
            service_id=service_id,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

        # ถ้ายังไม่มี count query
        total = len(rows)

        return rows, total
    