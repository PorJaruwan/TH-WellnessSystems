from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Currency
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class CurrencySearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Currency, search_fields=['currency_code', 'currency_name', 'currency_name_en', 'name_lo', 'name_en'])
