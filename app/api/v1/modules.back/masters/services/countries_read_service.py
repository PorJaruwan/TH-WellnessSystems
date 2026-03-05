from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.countries_read_repository import CountryReadRepository


class CountryReadService(BaseSettingsReadService):
    def __init__(self, repo: CountryReadRepository):
        super().__init__(repo=repo)
