from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.currencies_search_repository import CurrencySearchRepository


class CurrencySearchService(BaseSettingsSearchService):
    def __init__(self, repo: CurrencySearchRepository):
        super().__init__(repo=repo)
