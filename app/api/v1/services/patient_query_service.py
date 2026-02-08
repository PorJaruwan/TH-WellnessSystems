# app/api/v1/services/patient_query_service.py

from __future__ import annotations

from typing import Tuple, List, Optional
from sqlalchemy import select, func, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.patient_settings import Patient


SORT_MAP = {
    "created_at": Patient.created_at,
    "patient_code": Patient.patient_code,
    "full_name_lo": Patient.full_name_lo,
    "telephone": Patient.telephone,
    "status": Patient.status,
}


def _order_expr(sort_by: str, sort_order: str):
    col = SORT_MAP.get(sort_by, Patient.created_at)
    return desc(col) if sort_order == "desc" else asc(col)


async def list_patients(
    db: AsyncSession,
    *,
    is_active: Optional[bool] = True,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Tuple[List[Patient], int]:
    filters = []
    if is_active is not None:
        filters.append(Patient.is_active.is_(is_active))

    total_stmt = select(func.count()).select_from(Patient).where(*filters)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    stmt = (
        select(Patient)
        .where(*filters)
        .order_by(_order_expr(sort_by, sort_order))
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    items = res.scalars().all()
    return items, total


async def search_patients(
    db: AsyncSession,
    *,
    q_text: str,
    status: str = "",
    is_active: Optional[bool] = True,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Tuple[List[Patient], int]:
    filters = []

    if is_active is not None:
        filters.append(Patient.is_active.is_(is_active))

    if status:
        filters.append(Patient.status == status)

    q = (q_text or "").strip()
    if q:
        kw = f"%{q}%"
        filters.append(
            or_(
                Patient.first_name_lo.ilike(kw),
                Patient.last_name_lo.ilike(kw),
                func.coalesce(Patient.first_name_en, "").ilike(kw),
                func.coalesce(Patient.last_name_en, "").ilike(kw),
                Patient.patient_code.ilike(kw),
                func.coalesce(Patient.telephone, "").ilike(kw),
                Patient.id_card_no.ilike(kw),
            )
        )

    total_stmt = select(func.count()).select_from(Patient).where(*filters)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    stmt = (
        select(Patient)
        .where(*filters)
        .order_by(_order_expr(sort_by, sort_order))
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    items = res.scalars().all()
    return items, total
