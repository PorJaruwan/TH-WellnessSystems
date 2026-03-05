from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Geography
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsReadRepository


class GeographyReadRepository(BaseSettingsReadRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Geography, pk_field='id')
