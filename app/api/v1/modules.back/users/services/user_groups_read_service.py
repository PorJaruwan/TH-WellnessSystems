from __future__ import annotations

from app.api.v1.modules.users.repositories import UserGroupsRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class UserGroupsReadService:
    def __init__(self, repo: UserGroupsRepository | None = None):
        self.repo = repo or UserGroupsRepository()

    def get(self, *, id: str):
        return unwrap_single(self.repo.get_by_id(id))
