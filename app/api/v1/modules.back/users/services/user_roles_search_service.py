from __future__ import annotations

from app.api.v1.modules.users.repositories import UserRolesRepository
from app.api.v1.modules.users.services._utils import unwrap_supabase

class UserRolesSearchService:
    def __init__(self, repo: UserRolesRepository | None = None):
        self.repo = repo or UserRolesRepository()

    def search(self, *, limit: int = 50, offset: int = 0):
        res = self.repo.search(q="", q_field="", columns="*", order_by=None)
        rows = unwrap_supabase(res)
        total = len(rows)
        return rows[offset: offset + limit], total
