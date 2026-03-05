from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.services_read_repository import ServiceReadRepository


class ServiceReadService(BaseSettingsReadService):
    def __init__(self, repo: ServiceReadRepository):
        super().__init__(repo=repo)
