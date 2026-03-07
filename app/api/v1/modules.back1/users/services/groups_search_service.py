from __future__ import annotations

from app.api.v1.modules.users.repositories import GroupsRepository
from app.api.v1.modules.users.services._utils import unwrap_supabase

class GroupsSearchService:
    def __init__(self, repo: GroupsRepository | None = None):
        self.repo = repo or GroupsRepository()

    def search(self, *, q: str = "", limit: int = 50, offset: int = 0):
        res = self.repo.search(q=q, q_field="group_name", columns="*", order_by="group_name")
        rows = unwrap_supabase(res)
        total = len(rows)
        return rows[offset: offset + limit], total
