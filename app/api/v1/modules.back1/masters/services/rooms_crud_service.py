from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsCrudService
from app.api.v1.modules.masters.repositories.rooms_crud_repository import RoomCrudRepository


class RoomCrudService(BaseSettingsCrudService):
    def __init__(self, session: AsyncSession, repo: RoomCrudRepository):
        super().__init__(session=session, repo=repo)
