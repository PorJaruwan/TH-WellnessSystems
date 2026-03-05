from __future__ import annotations

from app.api.v1.modules.users.repositories import RolePermissionsRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class RolePermissionsReadService:
    def __init__(self, repo: RolePermissionsRepository | None = None):
        self.repo = repo or RolePermissionsRepository()

    def get(self, *, id: str):
        return unwrap_single(self.repo.get_by_id(id))
