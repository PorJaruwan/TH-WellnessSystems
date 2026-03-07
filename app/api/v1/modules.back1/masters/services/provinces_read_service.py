from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.provinces_read_repository import ProvinceReadRepository


class ProvinceReadService(BaseSettingsReadService):
    def __init__(self, repo: ProvinceReadRepository):
        super().__init__(repo=repo)
