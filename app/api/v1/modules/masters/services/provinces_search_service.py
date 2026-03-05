from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.provinces_search_repository import ProvinceSearchRepository


class ProvinceSearchService(BaseSettingsSearchService):
    def __init__(self, repo: ProvinceSearchRepository):
        super().__init__(repo=repo)

    async def search(
        self,
        q: str = "",
        country_code: str | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        return await self.repo.search(
            q=q,
            country_code=country_code,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )