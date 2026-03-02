from __future__ import annotations

from app.api.v1.modules.users.repositories import UserRolesRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class UserRolesReadService:
    def __init__(self, repo: UserRolesRepository | None = None):
        self.repo = repo or UserRolesRepository()

    def get(self, *, id: str):
        return unwrap_single(self.repo.get_by_id(id))
