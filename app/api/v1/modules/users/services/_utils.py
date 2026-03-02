from __future__ import annotations
from typing import Any, Tuple, List

def unwrap_supabase(res) -> list[dict]:
    # supabase-py response typically has .data
    data = getattr(res, "data", None)
    return data or []

def unwrap_single(res) -> dict | None:
    data = unwrap_supabase(res)
    return data[0] if data else None
