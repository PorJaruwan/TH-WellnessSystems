from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.districts_read_repository import DistrictReadRepository


class DistrictReadService(BaseSettingsReadService):
    def __init__(self, repo: DistrictReadRepository):
        super().__init__(repo=repo)
