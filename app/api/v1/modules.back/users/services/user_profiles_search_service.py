from __future__ import annotations

from app.api.v1.modules.users.repositories import UserProfilesRepository
from app.api.v1.modules.users.services._utils import unwrap_supabase

class UserProfilesSearchService:
    def __init__(self, repo: UserProfilesRepository | None = None):
        self.repo = repo or UserProfilesRepository()

    def search(self, *, q: str = "", limit: int = 50, offset: int = 0):
        res = self.repo.search_by_name(q=q)
        rows = unwrap_supabase(res)
        total = len(rows)
        return rows[offset: offset + limit], total
