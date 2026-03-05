from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsCrudService
from app.api.v1.modules.masters.repositories.languages_crud_repository import LanguageCrudRepository


class LanguageCrudService(BaseSettingsCrudService):
    def __init__(self, session: AsyncSession, repo: LanguageCrudRepository):
        super().__init__(session=session, repo=repo)
