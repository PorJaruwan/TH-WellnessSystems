from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.buildings_read_repository import BuildingReadRepository


class BuildingReadService(BaseSettingsReadService):
    def __init__(self, repo: BuildingReadRepository):
        super().__init__(repo=repo)
