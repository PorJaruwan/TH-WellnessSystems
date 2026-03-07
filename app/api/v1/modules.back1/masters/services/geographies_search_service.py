from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.geographies_search_repository import GeographySearchRepository


class GeographySearchService(BaseSettingsSearchService):
    def __init__(self, repo: GeographySearchRepository):
        super().__init__(repo=repo)
