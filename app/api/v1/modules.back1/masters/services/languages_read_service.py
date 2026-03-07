from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.languages_read_repository import LanguageReadRepository


class LanguageReadService(BaseSettingsReadService):
    def __init__(self, repo: LanguageReadRepository):
        super().__init__(repo=repo)
