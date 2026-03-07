from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.models as db_models

StaffDepartment = db_models.StaffDepartment
Staff = db_models.Staff
Department = getattr(db_models, "Department", getattr(db_models, "Departments", None))


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
        if Department is None:
            raise RuntimeError("Department model not found in app.db.models (expected Department or Departments)")

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

        cols = [
            StaffDepartment.id.label("id"),
            StaffDepartment.staff_id.label("staff_id"),
            StaffDepartment.department_id.label("department_id"),
            Staff.staff_name.label("staff_name"),
            Department.department_name.label("department_name"),
            getattr(StaffDepartment, "role_in_dept").label("role_in_dept") if hasattr(StaffDepartment, "role_in_dept") else None,
            getattr(StaffDepartment, "is_primary").label("is_primary") if hasattr(StaffDepartment, "is_primary") else None,
            getattr(StaffDepartment, "is_active").label("is_active") if hasattr(StaffDepartment, "is_active") else None,
            getattr(StaffDepartment, "created_at").label("created_at") if hasattr(StaffDepartment, "created_at") else None,
            getattr(StaffDepartment, "updated_at").label("updated_at") if hasattr(StaffDepartment, "updated_at") else None,
        ]
        cols = [c for c in cols if c is not None]

        stmt = (
            select(*cols)
            .select_from(StaffDepartment)
            .join(Staff, Staff.id == StaffDepartment.staff_id)
            .join(Department, Department.id == StaffDepartment.department_id)
        )

        for c in where:
            stmt = stmt.where(c)

        if hasattr(StaffDepartment, "created_at"):
            stmt = stmt.order_by(StaffDepartment.created_at.desc())
        else:
            stmt = stmt.order_by(StaffDepartment.id.desc())

        stmt = stmt.limit(limit).offset(offset)

        rows = (await self.db.execute(stmt)).mappings().all()
        return [dict(r) for r in rows], total
