from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RoomAvailability
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class RoomAvailabilitySearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=RoomAvailability, search_fields=['day_of_week', 'start_time', 'end_time'])
