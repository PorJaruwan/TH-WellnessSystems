from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.buildings_search_repository import BuildingSearchRepository


class BuildingSearchService(BaseSettingsSearchService):
    def __init__(self, repo: BuildingSearchRepository):
        super().__init__(repo=repo)
