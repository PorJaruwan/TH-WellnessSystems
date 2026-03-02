from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsCrudService
from app.api.v1.modules.masters.repositories.provinces_crud_repository import ProvinceCrudRepository


class ProvinceCrudService(BaseSettingsCrudService):
    def __init__(self, session: AsyncSession, repo: ProvinceCrudRepository):
        super().__init__(session=session, repo=repo)
