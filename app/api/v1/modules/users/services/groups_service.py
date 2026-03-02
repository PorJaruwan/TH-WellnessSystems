from __future__ import annotations

from app.api.v1.modules.users.repositories import GroupsRepository
from app.api.v1.modules.users.services._utils import unwrap_single

class GroupsService:
    def __init__(self, repo: GroupsRepository | None = None):
        self.repo = repo or GroupsRepository()

    def create(self, *, data: dict):
        return unwrap_single(self.repo.insert(data))

    def update(self, *, id: str, updated: dict):
        return unwrap_single(self.repo.update_by_id(id, updated))

    def delete(self, *, id: str):
        return unwrap_single(self.repo.delete_by_id(id))
