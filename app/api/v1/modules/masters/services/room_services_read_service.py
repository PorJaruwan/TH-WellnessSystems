from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.room_services_read_repository import RoomServiceReadRepository


class RoomServiceReadService(BaseSettingsReadService):
    def __init__(self, repo: RoomServiceReadRepository):
        super().__init__(repo=repo)
