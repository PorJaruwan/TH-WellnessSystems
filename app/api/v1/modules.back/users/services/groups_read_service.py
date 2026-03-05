from __future__ import annotations

from app.api.v1.modules.users.repositories import GroupsRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class GroupsReadService:
    def __init__(self, repo: GroupsRepository | None = None):
        self.repo = repo or GroupsRepository()

    def get(self, *, id: str):
        res = self.repo.get_by_id(id)
        return unwrap_single(res)
