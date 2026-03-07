from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.currencies_read_repository import CurrencyReadRepository


class CurrencyReadService(BaseSettingsReadService):
    def __init__(self, repo: CurrencyReadRepository):
        super().__init__(repo=repo)
