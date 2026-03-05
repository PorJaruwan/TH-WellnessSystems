
from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from app.api.v1.models._envelopes.base_envelopes import ListPayload, Paging, Sort
from app.api.v1.modules.patients.models.patients_model import (
    PatientImageCreate,
    PatientImageUpdate,
    PatientImageRead,
)
from app.api.v1.modules.patients.repositories.patient_images_repository import (
    PatientImagesRepository,
    DEFAULT_SORT_BY,
    DEFAULT_SORT_ORDER,
)


class PatientImagesService:
    def __init__(self, repo: PatientImagesRepository):
        self.repo = repo

    async def list(
        self,
        *,
        q: str = "",
        patient_id: Optional[UUID] = None,
        image_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = DEFAULT_SORT_BY,
        sort_order: str = DEFAULT_SORT_ORDER,
    ) -> Dict[str, Any]:
        items, total = await self.repo.list(
            q=q,
            patient_id=patient_id,
            image_type=image_type,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        typed_items = [PatientImageRead.model_validate(x) for x in items]

        payload = ListPayload[PatientImageRead](
            filters={"q": q or None, "patient_id": patient_id, "image_type": image_type},
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
        return {"payload": payload, "total": total}

    async def get(self, image_id: UUID) -> Optional[PatientImageRead]:
        obj = await self.repo.get_by_id(image_id)
        return PatientImageRead.model_validate(obj) if obj else None

    async def create(self, body: PatientImageCreate) -> PatientImageRead:
        from app.db.models.patient_settings import PatientImage

        obj = PatientImage(**body.model_dump())
        created = await self.repo.create(obj)
        return PatientImageRead.model_validate(created)

    async def update(self, image_id: UUID, body: PatientImageUpdate) -> Optional[PatientImageRead]:
        obj = await self.repo.get_by_id(image_id)
        if not obj:
            return None

        data = body.model_dump(exclude_unset=True, exclude_none=True)
        for k, v in data.items():
            setattr(obj, k, v)

        updated = await self.repo.update(obj)
        return PatientImageRead.model_validate(updated)

    async def delete(self, image_id: UUID) -> bool:
        obj = await self.repo.get_by_id(image_id)
        if not obj:
            return False
        await self.repo.delete(obj)
        return True
