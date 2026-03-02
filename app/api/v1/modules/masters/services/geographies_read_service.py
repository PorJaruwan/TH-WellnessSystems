from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.geographies_read_repository import GeographyReadRepository


class GeographyReadService(BaseSettingsReadService):
    def __init__(self, repo: GeographyReadRepository):
        super().__init__(repo=repo)
