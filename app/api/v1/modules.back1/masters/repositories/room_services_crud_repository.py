from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RoomService
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsCrudRepository


class RoomServiceCrudRepository(BaseSettingsCrudRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=RoomService, pk_field='id')
