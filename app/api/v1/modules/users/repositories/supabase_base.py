from __future__ import annotations

from typing import Any, Optional
from app.services.supabase_client import supabase

class SupabaseTableRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def insert(self, data: dict):
        return supabase.table(self.table_name).insert(data).execute()

    def update_by_id(self, id_value: str, updated: dict):
        return supabase.table(self.table_name).update(updated).eq("id", id_value).execute()

    def delete_by_id(self, id_value: str):
        return supabase.table(self.table_name).delete().eq("id", id_value).execute()

    def get_by_id(self, id_value: str, columns: str = "*"):
        return supabase.table(self.table_name).select(columns).eq("id", id_value).execute()

    def search(self, *, q: str = "", q_field: str = "", columns: str = "*", order_by: Optional[str] = None):
        query = supabase.table(self.table_name).select(columns)
        if q and q_field:
            query = query.ilike(q_field, f"%{q}%")
        if order_by:
            query = query.order(order_by, desc=False)
        return query.execute()
