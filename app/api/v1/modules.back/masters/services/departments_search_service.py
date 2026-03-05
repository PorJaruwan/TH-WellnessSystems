from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.departments_search_repository import DepartmentSearchRepository


class DepartmentSearchService(BaseSettingsSearchService):
    def __init__(self, repo: DepartmentSearchRepository):
        super().__init__(repo=repo)
