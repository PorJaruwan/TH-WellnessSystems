from __future__ import annotations

from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Staff


class StaffSearchRepository:
    """DB layer: search/list projection query only."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        q: str = "",
        role: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """Search staff (projection query).

        ✅ WellPlus standard:
        - search/list repo must return dict-like rows using .mappings().all()
        - service/DTO layer handles mapping/validation
        """
        where = []

        if hasattr(Staff, "is_active"):
            where.append(Staff.is_active == is_active)

        if role and hasattr(Staff, "role"):
            where.append(Staff.role == role)

        if q:
            kw = f"%{q}%"
            # use getattr with fallback to avoid runtime errors if a column is absent
            name_col = getattr(Staff, "staff_name", None)
            phone_col = getattr(Staff, "phone", None)
            email_col = getattr(Staff, "email", None)
            license_col = getattr(Staff, "license_number", None)
            specialty_col = getattr(Staff, "specialty", None)

            or_terms = []
            if name_col is not None:
                or_terms.append(name_col.ilike(kw))
            if phone_col is not None:
                or_terms.append(phone_col.ilike(kw))
            if email_col is not None:
                or_terms.append(email_col.ilike(kw))
            if license_col is not None:
                or_terms.append(func.coalesce(license_col, "").ilike(kw))
            if specialty_col is not None:
                or_terms.append(func.coalesce(specialty_col, "").ilike(kw))

            if or_terms:
                where.append(or_(*or_terms))

        # total count
        count_stmt = select(func.count()).select_from(Staff)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await self.db.execute(count_stmt)).scalar_one() or 0)

        # projection columns -> match StaffSearchItemDTO fields
        cols = []
        for col_name in [
            "id",
            "staff_name",
            "role",
            "phone",
            "email",
            "license_number",
            "specialty",
            "is_active",
        ]:
            col = getattr(Staff, col_name, None)
            if col is not None:
                cols.append(col)

        stmt = select(*cols) if cols else select(Staff)
        for c in where:
            stmt = stmt.where(c)

        order_col = getattr(Staff, "staff_name", None)
        if order_col is not None:
            stmt = stmt.order_by(order_col.asc())

        stmt = stmt.limit(limit).offset(offset)

        rows = (await self.db.execute(stmt)).mappings().all()
        items = [dict(r) for r in rows]
        return items, total
