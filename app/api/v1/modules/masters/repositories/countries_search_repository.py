from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Country
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class CountrySearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Country, search_fields=['country_code', 'name_lo', 'name_en', 'country_name', 'country_name_en'])
