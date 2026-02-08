# app/api/v1/services/patient_images_service.py
from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.patient_settings import PatientImage
from app.api.v1.models.patients_model import (
    PatientImageCreate,
    PatientImageUpdate,
    PatientImageRead,
)


# -----------------------------
# Sorting
# -----------------------------
_ALLOWED_SORT_FIELDS = {
    "created_at": PatientImage.created_at,
    "updated_at": PatientImage.updated_at,
    "image_type": PatientImage.image_type,
    "patient_id": PatientImage.patient_id,
    "file_path": PatientImage.file_path,
}

_DEFAULT_SORT = "-created_at"  # ใหม่สุดก่อน (เหมาะกับ images)


def _apply_sort(stmt, sort: str):
    """
    sort format:
      -created_at  (desc)
      created_at   (asc)
    """
    sort = (sort or _DEFAULT_SORT).strip()

    desc = sort.startswith("-")
    field_key = sort[1:] if desc else sort

    col = _ALLOWED_SORT_FIELDS.get(field_key)
    if col is None:
        # ถ้า field ไม่ถูกต้อง -> fallback เป็น default
        col = _ALLOWED_SORT_FIELDS["created_at"]
        desc = True

    return stmt.order_by(col.desc() if desc else col.asc())


def _to_read(obj: PatientImage) -> dict:
    return PatientImageRead.model_validate(obj).model_dump()


# -----------------------------
# CRUD
# -----------------------------
async def create_patient_image(db: AsyncSession, payload: PatientImageCreate) -> dict:
    obj = PatientImage(**payload.model_dump(exclude_none=True))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return _to_read(obj)


async def get_patient_image_by_id(db: AsyncSession, image_id: UUID) -> Optional[dict]:
    res = await db.execute(select(PatientImage).where(PatientImage.id == image_id))
    obj = res.scalar_one_or_none()
    return _to_read(obj) if obj else None


async def update_patient_image_by_id(db: AsyncSession, image_id: UUID, payload: PatientImageUpdate) -> Optional[dict]:
    res = await db.execute(select(PatientImage).where(PatientImage.id == image_id))
    obj = res.scalar_one_or_none()
    if not obj:
        return None

    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for k, v in updates.items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return _to_read(obj)


async def delete_patient_image_by_id(db: AsyncSession, image_id: UUID) -> bool:
    res = await db.execute(select(PatientImage).where(PatientImage.id == image_id))
    obj = res.scalar_one_or_none()
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True


# -----------------------------
# LIST  (DB paging + filter + sort)
# -----------------------------
async def list_patient_images(
    db: AsyncSession,
    q: str = "",
    patient_id: Optional[UUID] = None,
    image_type: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: str = _DEFAULT_SORT,
) -> Tuple[List[dict], int]:
    filters = []

    if patient_id:
        filters.append(PatientImage.patient_id == patient_id)

    if image_type:
        filters.append(PatientImage.image_type == image_type)

    if q:
        kw = f"%{q}%"
        filters.append(
            or_(
                PatientImage.file_path.ilike(kw),
                func.coalesce(PatientImage.description, "").ilike(kw),
                func.coalesce(PatientImage.image_type, "").ilike(kw),
            )
        )

    # total
    total_stmt = select(func.count()).select_from(PatientImage)
    if filters:
        total_stmt = total_stmt.where(*filters)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    # items
    stmt = select(PatientImage)
    if filters:
        stmt = stmt.where(*filters)

    stmt = _apply_sort(stmt, sort).limit(limit).offset(offset)

    res = await db.execute(stmt)
    items = [_to_read(x) for x in res.scalars().all()]
    return items, total
