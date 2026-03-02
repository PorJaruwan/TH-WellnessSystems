from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.rooms_read_repository import RoomReadRepository


class RoomReadService(BaseSettingsReadService):
    def __init__(self, repo: RoomReadRepository):
        super().__init__(repo=repo)
