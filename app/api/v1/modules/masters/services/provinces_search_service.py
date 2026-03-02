from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.provinces_search_repository import ProvinceSearchRepository


class ProvinceSearchService(BaseSettingsSearchService):
    def __init__(self, repo: ProvinceSearchRepository):
        super().__init__(repo=repo)
