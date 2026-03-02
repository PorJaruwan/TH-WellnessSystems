from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import City
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsReadRepository


class CityReadRepository(BaseSettingsReadRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=City, pk_field='id')
