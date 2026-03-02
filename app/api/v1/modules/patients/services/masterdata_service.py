# app/api/v1/modules/patients/services/masterdata_service.py

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple, Type

from app.api.v1.models._envelopes.base_envelopes import ListPayload, Paging, Sort
from app.api.v1.modules.patients.repositories.masterdata_repository import MasterDataRepository


class MasterDataService:
    """Generic service for patient master-data modules."""

    def __init__(self, repo: MasterDataRepository):
        self.repo = repo

    async def search_list_payload(
        self,
        *,
        model: Type[Any],
        dto: Type[Any],
        q: Optional[str],
        is_active: Optional[bool],
        search_fields: Sequence[str],
        extra_eq_filters: Optional[Dict[str, Any]] = None,
        sort_by: str,
        sort_order: str,
        allowed_sort_fields: Sequence[str],
        default_sort_by: str,
        limit: int,
        offset: int,
        filters_payload: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ListPayload[Any], int, str]:
        """Return (ListPayload, total, effective_sort_by)."""

        items, total, effective_sort_by = await self.repo.search(
            model=model,
            q=q,
            search_fields=search_fields,
            is_active=is_active,
            extra_eq_filters=extra_eq_filters,
            sort_by=sort_by,
            sort_order=sort_order,
            allowed_sort_fields=allowed_sort_fields,
            default_sort_by=default_sort_by,
            limit=limit,
            offset=offset,
        )

        typed_items = [dto.model_validate(x) for x in items]

        paging = Paging(
            total=total,
            limit=limit,
            offset=offset,
            returned=len(typed_items),
            has_more=(offset + limit) < total,
            next_offset=(offset + limit) if (offset + limit) < total else None,
        )

        payload = ListPayload[Any](
            filters=filters_payload or {"q": q, "is_active": is_active},
            sort=Sort(by=effective_sort_by, order=sort_order),
            paging=paging,
            items=typed_items,
        )

        return payload, total, effective_sort_by
