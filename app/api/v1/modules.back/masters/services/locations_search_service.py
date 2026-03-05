from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.locations_search_repository import LocationSearchRepository


class LocationSearchService(BaseSettingsSearchService):
    def __init__(self, repo: LocationSearchRepository):
        super().__init__(repo=repo)
