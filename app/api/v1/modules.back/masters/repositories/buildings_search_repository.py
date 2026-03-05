from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Building
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class BuildingSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Building, search_fields=['building_code', 'building_name', 'building_name_en', 'name_lo', 'name_en'])
