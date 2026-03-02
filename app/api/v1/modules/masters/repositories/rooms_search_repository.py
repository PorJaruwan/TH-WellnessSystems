from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Room
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class RoomSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Room, search_fields=['room_code', 'room_name', 'room_name_en', 'name_lo', 'name_en'])
