# app/api/v1/utils/list_payload_builder.py

from __future__ import annotations

from typing import Any, Optional

from app.api.v1.models._envelopes.base_envelopes import (
    ListPayload,
    Paging,
    Sort,
)


def build_list_payload(
    *,
    items: list[Any],
    total: int,
    limit: int,
    offset: int,
    filters: Optional[dict] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
):
    """
    Standard builder for ListPayload
    Used by ALL search/list endpoints.
    """

    returned = len(items)
    has_more = (offset + returned) < total
    next_offset = (offset + returned) if has_more else None

    return ListPayload(
        filters=filters or {},
        sort=Sort(by=sort_by, order=sort_order) if sort_by else None,
        paging=Paging(
            total=total,
            limit=limit,
            offset=offset,
            returned=returned,
            has_more=has_more,
            next_offset=next_offset,
        ),
        items=items,
    )