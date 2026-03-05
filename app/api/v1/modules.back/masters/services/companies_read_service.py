from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.companies_read_repository import CompanyReadRepository


class CompanyReadService(BaseSettingsReadService):
    def __init__(self, repo: CompanyReadRepository):
        super().__init__(repo=repo)
