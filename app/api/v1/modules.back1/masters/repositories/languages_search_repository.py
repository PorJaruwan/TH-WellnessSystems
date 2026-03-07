from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Language
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class LanguageSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Language, search_fields=['language_code', 'language_name', 'language_name_en', 'name_lo', 'name_en'])
