from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Service
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class ServiceSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Service, search_fields=['service_code', 'service_name', 'service_name_en', 'name_lo', 'name_en'])
