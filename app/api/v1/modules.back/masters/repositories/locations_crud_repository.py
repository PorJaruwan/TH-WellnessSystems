from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Location
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsCrudRepository


class LocationCrudRepository(BaseSettingsCrudRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Location, pk_field='id')
