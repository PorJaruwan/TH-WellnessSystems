from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.patient_settings import Patient, Source


class PatientsSearchRepository:
    """Projection-only repository for Patients search.

    ✅ MUST NOT return ORM objects
    ✅ MUST NOT touch relationships (avoid lazy-load)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_projection(
        self,
        *,
        q_text: str = "",
        status: str = "",
        source_type: str = "",
        is_active: Optional[bool] = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Dict[str, Any]], int]:
        filters = []

        if is_active is not None:
            filters.append(Patient.is_active.is_(is_active))

        if q_text:
            kw = f"%{q_text}%"
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

        if status:
            filters.append(Patient.status == status)

        if source_type:
            src_ids_subq = select(Source.id).where(Source.source_type == source_type)
            filters.append(
                or_(
                    Patient.source_id.in_(src_ids_subq),
                    Patient.market_source_id.in_(src_ids_subq),
                )
            )

        # total
        total_stmt = select(func.count()).select_from(Patient).where(*filters)
        total = int((await self.db.execute(total_stmt)).scalar() or 0)

        # allowlist sort
        sort_col = getattr(Patient, sort_by, Patient.created_at)
        sort_expr = sort_col.asc() if sort_order == "asc" else sort_col.desc()

        stmt = (
            select(
                Patient.id,
                Patient.patient_code,
                Patient.full_name_lo,
                Patient.full_name_en,
                Patient.telephone,
                Patient.status,
                Patient.is_active,
            )
            .where(*filters)
            .order_by(sort_expr)
            .limit(limit)
            .offset(offset)
        )

        rows = (await self.db.execute(stmt)).all()

        items = [
            {
                "id": r.id,
                "patient_code": r.patient_code,
                "full_name_lo": r.full_name_lo,
                "full_name_en": r.full_name_en,
                "telephone": r.telephone,
                "status": r.status,
                "is_active": r.is_active,
            }
            for r in rows
        ]

        return items, total
