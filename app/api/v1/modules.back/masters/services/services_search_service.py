from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.services_search_repository import ServiceSearchRepository


class ServiceSearchService(BaseSettingsSearchService):
    def __init__(self, repo: ServiceSearchRepository):
        super().__init__(repo=repo)
