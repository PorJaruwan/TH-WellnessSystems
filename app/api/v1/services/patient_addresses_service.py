# app/api/v1/services/patient_addresses_service.py

from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.patient_settings import PatientAddress


SORT_MAP = {
    "address_type": PatientAddress.address_type,
    "city": PatientAddress.city,
    "state_province": PatientAddress.state_province,
    "postal_code": PatientAddress.postal_code,
    "is_primary": PatientAddress.is_primary,
    "created_at": PatientAddress.created_at,
    "updated_at": PatientAddress.updated_at,
}


def _order_expr(sort_by: str, sort_order: str):
    col = SORT_MAP.get(sort_by, PatientAddress.address_type)
    return desc(col) if sort_order == "desc" else asc(col)


async def list_patient_addresses(
    db: AsyncSession,
    *,
    q: str = "",
    patient_id: Optional[UUID] = None,
    address_type: str = "",
    is_primary: Optional[bool] = None,
    limit: int = 200,
    offset: int = 0,
    sort_by: str = "address_type",
    sort_order: str = "asc",
) -> Tuple[List[PatientAddress], int]:
    filters = []

    if patient_id is not None:
        filters.append(PatientAddress.patient_id == patient_id)

    if address_type:
        filters.append(PatientAddress.address_type == address_type)

    if is_primary is not None:
        filters.append(PatientAddress.is_primary.is_(is_primary))

    q2 = (q or "").strip()
    if q2:
        kw = f"%{q2}%"
        filters.append(
            or_(
                PatientAddress.address_line1.ilike(kw),
                func.coalesce(PatientAddress.address_line2, "").ilike(kw),
                func.coalesce(PatientAddress.sub_district, "").ilike(kw),
                func.coalesce(PatientAddress.city, "").ilike(kw),
                func.coalesce(PatientAddress.state_province, "").ilike(kw),
                func.coalesce(PatientAddress.postal_code, "").ilike(kw),
                func.coalesce(PatientAddress.full_address_lo, "").ilike(kw),
                func.coalesce(PatientAddress.full_address_en, "").ilike(kw),
            )
        )

    total_stmt = select(func.count()).select_from(PatientAddress).where(*filters)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    stmt = (
        select(PatientAddress)
        .where(*filters)
        .order_by(_order_expr(sort_by, sort_order))
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    items = list(res.scalars().all())
    return items, total


async def get_patient_address(
    db: AsyncSession,
    *,
    patient_id: UUID,
    address_type: str,
) -> Optional[PatientAddress]:
    stmt = select(PatientAddress).where(
        PatientAddress.patient_id == patient_id,
        PatientAddress.address_type == address_type,
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create_patient_address(
    db: AsyncSession,
    obj: PatientAddress,
) -> PatientAddress:
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_patient_address(
    db: AsyncSession,
    *,
    patient_id: UUID,
    address_type: str,
    updates: dict,
) -> Optional[PatientAddress]:
    obj = await get_patient_address(db, patient_id=patient_id, address_type=address_type)
    if not obj:
        return None

    for k, v in updates.items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_patient_address(
    db: AsyncSession,
    *,
    patient_id: UUID,
    address_type: str,
) -> bool:
    obj = await get_patient_address(db, patient_id=patient_id, address_type=address_type)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
