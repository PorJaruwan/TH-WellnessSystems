from __future__ import annotations

from app.api.v1.modules.users.repositories import UserProfilesRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class UserProfilesReadService:
    def __init__(self, repo: UserProfilesRepository | None = None):
        self.repo = repo or UserProfilesRepository()

    def get(self, *, id: str):
        res = self.repo.get_by_id(id)
        return unwrap_single(res)
