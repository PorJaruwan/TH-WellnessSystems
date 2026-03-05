from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.districts_search_repository import DistrictSearchRepository


class DistrictSearchService(BaseSettingsSearchService):
    def __init__(self, repo: DistrictSearchRepository):
        super().__init__(repo=repo)

    async def search(
        self,
        q: str = "",
        zip_code_exact: int | None = None,
        city_id: int | None = None,
        province_id: int | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        return await self.repo.search(
            q=q,
            zip_code_exact=zip_code_exact,
            city_id=city_id,
            province_id=province_id,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )