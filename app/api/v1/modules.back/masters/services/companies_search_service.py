from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.companies_search_repository import CompanySearchRepository


class CompanySearchService(BaseSettingsSearchService):
    def __init__(self, repo: CompanySearchRepository):
        super().__init__(repo=repo)
