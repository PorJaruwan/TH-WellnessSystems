from __future__ import annotations

from app.api.v1.modules.masters.services.base_settings_service import BaseSettingsReadService
from app.api.v1.modules.masters.repositories.service_types_read_repository import ServiceTypeReadRepository


class ServiceTypeReadService(BaseSettingsReadService):
    def __init__(self, repo: ServiceTypeReadRepository):
        super().__init__(repo=repo)
