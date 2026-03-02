from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import District
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class DistrictSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=District, search_fields=['name_lo', 'name_en'])
