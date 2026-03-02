from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsSearchService
from app.api.v1.modules.masters.repositories.room_availabilities_search_repository import RoomAvailabilitySearchRepository


class RoomAvailabilitySearchService(BaseSettingsSearchService):
    def __init__(self, repo: RoomAvailabilitySearchRepository):
        super().__init__(repo=repo)
