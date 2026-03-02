from __future__ import annotations

from app.api.v1.modules.users.repositories import PermissionsRepository
from app.api.v1.modules.users.services._utils import unwrap_supabase

class PermissionsSearchService:
    def __init__(self, repo: PermissionsRepository | None = None):
        self.repo = repo or PermissionsRepository()

    def search(self, *, q: str = "", limit: int = 50, offset: int = 0):
        res = self.repo.search(q=q, q_field="permission_code", columns="*", order_by="permission_code")
        rows = unwrap_supabase(res)
        total = len(rows)
        return rows[offset: offset + limit], total
