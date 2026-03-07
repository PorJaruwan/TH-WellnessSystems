from __future__ import annotations

from app.api.v1.modules.users.repositories import GroupRolesRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class GroupRolesReadService:
    def __init__(self, repo: GroupRolesRepository | None = None):
        self.repo = repo or GroupRolesRepository()

    def get(self, *, id: str):
        return unwrap_single(self.repo.get_by_id(id))
