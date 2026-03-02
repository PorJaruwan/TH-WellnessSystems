from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.countries_search_repository import CountrySearchRepository


class CountrySearchService(BaseSettingsSearchService):
    def __init__(self, repo: CountrySearchRepository):
        super().__init__(repo=repo)
