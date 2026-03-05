from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Company
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class CompanySearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Company, search_fields=['company_code', 'company_name', 'company_name_en'])
