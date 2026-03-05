from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Location
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class LocationSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Location, search_fields=['location_code', 'location_name', 'location_name_en', 'name_lo', 'name_en'])
