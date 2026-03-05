from __future__ import annotations

from typing import Optional

from app.api.v1.models._envelopes.base_envelopes import ListPayload, Paging, Sort
from app.api.v1.modules.patients.models.dtos import PatientSearchItemDTO
from app.api.v1.modules.patients.repositories.patients_search_repository import PatientsSearchRepository


class PatientsSearchService:
    """Business layer for Patients search/list."""

    def __init__(self, repo: PatientsSearchRepository):
        self.repo = repo

    async def search(
        self,
        *,
        q: str = "",
        status: str = "",
        source_type: str = "",
        is_active: Optional[bool] = True,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ListPayload[PatientSearchItemDTO], int, dict]:
        items, total = await self.repo.search_projection(
            q_text=q,
            status=status,
            source_type=source_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        typed_items = [PatientSearchItemDTO.model_validate(x) for x in items]

        payload = ListPayload[PatientSearchItemDTO](
            filters={
                "q": q or None,
                "status": status or None,
                "is_active": is_active,
                "source_type": source_type or None,
            },
            sort=Sort(by=sort_by, order=sort_order),
            paging=Paging(
                total=total,
                limit=limit,
                offset=offset,
                returned=len(typed_items),
                has_more=(offset + limit) < total,
                next_offset=(offset + limit) if (offset + limit) < total else None,
            ),
            items=typed_items,
        )

        return payload, total, payload.filters
