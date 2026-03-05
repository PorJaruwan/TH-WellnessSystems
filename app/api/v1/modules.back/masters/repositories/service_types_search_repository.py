from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ServiceType
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class ServiceTypeSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=ServiceType, search_fields=['service_type_code', 'service_type_name', 'service_type_name_en', 'name_lo', 'name_en'])
