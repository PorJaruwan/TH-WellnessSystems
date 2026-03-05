from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.service_types_search_repository import ServiceTypeSearchRepository


class ServiceTypeSearchService(BaseSettingsSearchService):
    def __init__(self, repo: ServiceTypeSearchRepository):
        super().__init__(repo=repo)
