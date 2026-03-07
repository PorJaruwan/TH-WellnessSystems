from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Geography
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class GeographySearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Geography, search_fields=['name_lo', 'name_en'])
