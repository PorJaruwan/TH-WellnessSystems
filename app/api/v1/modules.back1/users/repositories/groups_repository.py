from __future__ import annotations
from app.api.v1.modules.users.repositories.supabase_base import SupabaseTableRepository

class GroupsRepository(SupabaseTableRepository):
    def __init__(self):
        super().__init__("groups")
