from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.locations_read_repository import LocationReadRepository


class LocationReadService(BaseSettingsReadService):
    def __init__(self, repo: LocationReadRepository):
        super().__init__(repo=repo)
