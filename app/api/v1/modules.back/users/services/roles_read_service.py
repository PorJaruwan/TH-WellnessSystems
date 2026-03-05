from __future__ import annotations

from app.api.v1.modules.users.repositories import RolesRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class RolesReadService:
    def __init__(self, repo: RolesRepository | None = None):
        self.repo = repo or RolesRepository()

    def get(self, *, id: str):
        res = self.repo.get_by_id(id)
        return unwrap_single(res)
