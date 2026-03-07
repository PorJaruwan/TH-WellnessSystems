from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsCrudService
from app.api.v1.modules.masters.repositories.districts_crud_repository import DistrictCrudRepository


class DistrictCrudService(BaseSettingsCrudService):
    def __init__(self, session: AsyncSession, repo: DistrictCrudRepository):
        super().__init__(session=session, repo=repo)
