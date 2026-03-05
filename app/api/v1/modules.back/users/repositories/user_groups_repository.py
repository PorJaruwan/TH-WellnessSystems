from __future__ import annotations
from app.api.v1.modules.users.repositories.supabase_base import SupabaseTableRepository

class UserGroupsRepository(SupabaseTableRepository):
    def __init__(self):
        super().__init__("user_groups")
