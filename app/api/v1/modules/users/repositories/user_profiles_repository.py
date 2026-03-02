from __future__ import annotations
from app.api.v1.modules.users.repositories.supabase_base import SupabaseTableRepository

class UserProfilesRepository(SupabaseTableRepository):
    def __init__(self):
        super().__init__("user_profiles")

    def search_by_name(self, q: str = ""):
        # projection for list/search
        return self.search(
            q=q,
            q_field="full_name",
            columns="id, full_name, email, user_id, company_code, location_id, department_id, preferred_language, preferred_currency, is_active, created_at, updated_at",
            order_by="full_name",
        )
