from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.cities_read_repository import CityReadRepository


class CityReadService(BaseSettingsReadService):
    def __init__(self, repo: CityReadRepository):
        super().__init__(repo=repo)
