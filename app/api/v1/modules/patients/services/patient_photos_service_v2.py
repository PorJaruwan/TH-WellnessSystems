
from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from app.api.v1.models._envelopes.base_envelopes import ListPayload, Paging, Sort
from app.api.v1.modules.patients.models.patient_photos_models import PatientPhotoRead
from app.api.v1.modules.patients.repositories.patient_photos_repository import (
    PatientPhotosRepository,
    DEFAULT_SORT_BY,
    DEFAULT_SORT_ORDER,
)
from app.api.v1.modules.patients.services.patient_photos_storage_service import (
    upload_patient_photo_to_storage,
    remove_patient_photo_from_storage,
)


class PatientPhotosService:
    """Patient photos: upload to storage + store record in PatientImage table."""

    def __init__(self, repo: PatientPhotosRepository):
        self.repo = repo

    def _to_read(self, obj) -> PatientPhotoRead:
        # ✅ PatientImage.created_at -> uploaded_at
        return PatientPhotoRead(
            id=obj.id,
            patient_id=obj.patient_id,
            file_path=obj.file_path,
            uploaded_at=getattr(obj, "created_at"),
        )

    async def list(
        self,
        *,
        q: str = "",
        patient_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = DEFAULT_SORT_BY,
        sort_order: str = DEFAULT_SORT_ORDER,
    ) -> Dict[str, Any]:
        items, total = await self.repo.list(
            q=q,
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        typed_items = [self._to_read(x) for x in items]

        payload = ListPayload[PatientPhotoRead](
            filters={"q": q or None, "patient_id": patient_id},
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

    async def get(self, photo_id: UUID) -> Optional[PatientPhotoRead]:
        obj = await self.repo.get_by_id(photo_id)
        return self._to_read(obj) if obj else None

    async def get_by_patient(self, patient_id: UUID) -> Optional[PatientPhotoRead]:
        obj = await self.repo.get_latest_by_patient(patient_id)
        return self._to_read(obj) if obj else None

    async def upload(self, *, patient_id: UUID, file_bytes: bytes, original_filename: str, content_type: str) -> Dict[str, Any]:
        # 1) upload to storage (supabase bucket)
        file_url = upload_patient_photo_to_storage(
            patient_id=patient_id,
            file_bytes=file_bytes,
            original_filename=original_filename,
            content_type=content_type,
        )

        # 2) store record in DB (PatientImage)
        from app.db.models.patient_settings import PatientImage

        obj = PatientImage(
            patient_id=patient_id,
            file_path=file_url,
            image_type=content_type,
            description="photo",
        )
        created = await self.repo.create(obj)
        return {"id": created.id, "patient_id": patient_id, "file_path": created.file_path}

    async def delete(self, photo_id: UUID) -> bool:
        obj = await self.repo.get_by_id(photo_id)
        if not obj:
            return False

        # delete file from storage first (best-effort)
        try:
            remove_patient_photo_from_storage(obj.file_path)
        except Exception:
            # ✅ don't block DB delete (storage may already be removed)
            pass

        await self.repo.delete(obj)
        return True
