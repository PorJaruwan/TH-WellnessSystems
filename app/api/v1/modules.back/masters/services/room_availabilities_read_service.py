from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.room_availabilities_read_repository import RoomAvailabilityReadRepository


class RoomAvailabilityReadService(BaseSettingsReadService):
    def __init__(self, repo: RoomAvailabilityReadRepository):
        super().__init__(repo=repo)
