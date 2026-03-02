from __future__ import annotations

from app.api.v1.modules.users.repositories import RolesRepository
from app.api.v1.modules.users.services._utils import unwrap_supabase

class RolesSearchService:
    def __init__(self, repo: RolesRepository | None = None):
        self.repo = repo or RolesRepository()

    def search(self, *, q: str = "", limit: int = 50, offset: int = 0):
        res = self.repo.search(q=q, q_field="role_name", columns="*", order_by="role_name")
        rows = unwrap_supabase(res)
        total = len(rows)
        return rows[offset: offset + limit], total
