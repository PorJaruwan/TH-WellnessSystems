from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import StaffDepartment


class StaffDepartmentsSearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        staff_id: Optional[UUID] = None,
        department_id: Optional[UUID] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        where = []
        if staff_id:
            where.append(StaffDepartment.staff_id == staff_id)
        if department_id:
            where.append(StaffDepartment.department_id == department_id)
        if hasattr(StaffDepartment, "is_active"):
            where.append(StaffDepartment.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffDepartment)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await self.db.execute(count_stmt)).scalar_one() or 0)

        stmt = select(
            StaffDepartment.id.label("id"),
            StaffDepartment.staff_id.label("staff_id"),
            StaffDepartment.department_id.label("department_id"),
            getattr(StaffDepartment, "role_in_dept").label("role_in_dept") if hasattr(StaffDepartment, "role_in_dept") else None,
            getattr(StaffDepartment, "is_primary").label("is_primary") if hasattr(StaffDepartment, "is_primary") else None,
            getattr(StaffDepartment, "is_active").label("is_active") if hasattr(StaffDepartment, "is_active") else None,
            getattr(StaffDepartment, "created_at").label("created_at") if hasattr(StaffDepartment, "created_at") else None,
            getattr(StaffDepartment, "updated_at").label("updated_at") if hasattr(StaffDepartment, "updated_at") else None,
        )

        # remove None columns
        stmt = select(*[c for c in stmt.selected_columns if c is not None])

        for c in where:
            stmt = stmt.where(c)

        if hasattr(StaffDepartment, "created_at"):
            stmt = stmt.order_by(StaffDepartment.created_at.desc())
        else:
            stmt = stmt.order_by(StaffDepartment.id.desc())

        stmt = stmt.limit(limit).offset(offset)

        rows = (await self.db.execute(stmt)).mappings().all()
        return [dict(r) for r in rows], total
