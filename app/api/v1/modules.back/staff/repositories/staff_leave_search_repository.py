from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import StaffLeave


class StaffLeaveSearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        company_code: Optional[str] = None,
        location_id: Optional[UUID] = None,
        staff_id: Optional[UUID] = None,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        where = []
        if company_code:
            where.append(StaffLeave.company_code == company_code)
        if location_id:
            where.append(StaffLeave.location_id == location_id)
        if staff_id:
            where.append(StaffLeave.staff_id == staff_id)
        if status:
            where.append(StaffLeave.status == status)
        if date_from and date_to:
            # overlap
            where.append(and_(StaffLeave.date_to >= date_from, StaffLeave.date_from <= date_to))
        elif date_from:
            where.append(StaffLeave.date_to >= date_from)
        elif date_to:
            where.append(StaffLeave.date_from <= date_to)

        if hasattr(StaffLeave, "is_active"):
            where.append(StaffLeave.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffLeave)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await self.db.execute(count_stmt)).scalar_one() or 0)

        stmt = select(
            StaffLeave.id.label("id"),
            StaffLeave.company_code.label("company_code"),
            StaffLeave.location_id.label("location_id"),
            StaffLeave.staff_id.label("staff_id"),
            StaffLeave.leave_type.label("leave_type"),
            StaffLeave.date_from.label("date_from"),
            StaffLeave.date_to.label("date_to"),
            getattr(StaffLeave, "part_of_day").label("part_of_day") if hasattr(StaffLeave, "part_of_day") else None,
            StaffLeave.status.label("status"),
            getattr(StaffLeave, "reason").label("reason") if hasattr(StaffLeave, "reason") else None,
            getattr(StaffLeave, "approved_at").label("approved_at") if hasattr(StaffLeave, "approved_at") else None,
            getattr(StaffLeave, "approved_by").label("approved_by") if hasattr(StaffLeave, "approved_by") else None,
            getattr(StaffLeave, "is_active").label("is_active") if hasattr(StaffLeave, "is_active") else None,
            getattr(StaffLeave, "created_at").label("created_at") if hasattr(StaffLeave, "created_at") else None,
            getattr(StaffLeave, "updated_at").label("updated_at") if hasattr(StaffLeave, "updated_at") else None,
        )
        stmt = select(*[c for c in stmt.selected_columns if c is not None])

        for c in where:
            stmt = stmt.where(c)

        if hasattr(StaffLeave, "created_at"):
            stmt = stmt.order_by(StaffLeave.created_at.desc())
        else:
            stmt = stmt.order_by(StaffLeave.id.desc())

        stmt = stmt.limit(limit).offset(offset)

        rows = (await self.db.execute(stmt)).mappings().all()
        return [dict(r) for r in rows], total
