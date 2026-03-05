from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsCrudService
from app.api.v1.modules.masters.repositories.companies_crud_repository import CompanyCrudRepository


class CompanyCrudService(BaseSettingsCrudService):
    def __init__(self, session: AsyncSession, repo: CompanyCrudRepository):
        super().__init__(session=session, repo=repo)
