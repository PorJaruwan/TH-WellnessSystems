from __future__ import annotations

from app.api.v1.modules.users.repositories import PermissionsRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class PermissionsReadService:
    def __init__(self, repo: PermissionsRepository | None = None):
        self.repo = repo or PermissionsRepository()

    def get(self, *, id: str):
        res = self.repo.get_by_id(id)
        return unwrap_single(res)
