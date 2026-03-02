from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.departments_read_repository import DepartmentReadRepository


class DepartmentReadService(BaseSettingsReadService):
    def __init__(self, repo: DepartmentReadRepository):
        super().__init__(repo=repo)
