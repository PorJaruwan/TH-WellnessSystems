# app/api/v1/utils/masterdata_filter.py

from __future__ import annotations
from typing import Any, List, Optional


def _get_value(item: Any, field: str) -> str:
    if isinstance(item, dict):
        v = item.get(field, "")
    else:
        v = getattr(item, field, "")
    return "" if v is None else str(v)


def _get_bool(item: Any, field: str) -> Optional[bool]:
    if isinstance(item, dict):
        return item.get(field, None)
    return getattr(item, field, None)


def filter_masterdata_in_memory(
    items: List[Any],
    *,
    q: Optional[str],
    is_active: Optional[bool],
    search_fields: List[str],
) -> List[Any]:
    out = items or []

    if q:
        q2 = q.strip().lower()

        def match(x: Any) -> bool:
            for f in search_fields:
                if q2 in _get_value(x, f).lower():
                    return True
            return False

        out = [x for x in out if match(x)]

    if is_active is not None:
        out = [x for x in out if _get_bool(x, "is_active") is is_active]

    return out


def page_items(items: List[Any], limit: int, offset: int) -> List[Any]:
    if limit <= 0:
        return []
    return (items or [])[offset : offset + limit]
