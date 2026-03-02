from __future__ import annotations

from app.api.v1.modules.users.repositories import UserProfilesRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class UserProfilesService:
    def __init__(self, repo: UserProfilesRepository | None = None):
        self.repo = repo or UserProfilesRepository()

    def create(self, *, data: dict):
        res = self.repo.insert(data)
        return unwrap_single(res)

    def update(self, *, id: str, updated: dict):
        res = self.repo.update_by_id(id, updated)
        return unwrap_single(res)

    def delete(self, *, id: str):
        res = self.repo.delete_by_id(id)
        # supabase delete returns deleted rows in .data usually
        return unwrap_single(res)
