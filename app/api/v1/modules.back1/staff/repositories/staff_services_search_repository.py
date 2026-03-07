from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.models as db_models

StaffService = db_models.StaffService
Staff = db_models.Staff
Service = getattr(db_models, "Service", getattr(db_models, "Services", None))


class StaffServicesSearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        staff_id: Optional[UUID] = None,
        service_id: Optional[UUID] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        if Service is None:
            raise RuntimeError("Service model not found in app.db.models (expected Service or Services)")

        where = []
        if staff_id:
            where.append(StaffService.staff_id == staff_id)
        if service_id:
            where.append(StaffService.service_id == service_id)
        if hasattr(StaffService, "is_active"):
            where.append(StaffService.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffService)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await self.db.execute(count_stmt)).scalar_one() or 0)

        cols = [
            StaffService.id.label("id"),
            StaffService.staff_id.label("staff_id"),
            StaffService.service_id.label("service_id"),
            Staff.staff_name.label("staff_name"),
            Service.service_name.label("service_name"),
            getattr(StaffService, "duration_minutes").label("duration_minutes") if hasattr(StaffService, "duration_minutes") else None,
            getattr(StaffService, "is_active").label("is_active") if hasattr(StaffService, "is_active") else None,
            getattr(StaffService, "created_at").label("created_at") if hasattr(StaffService, "created_at") else None,
            getattr(StaffService, "updated_at").label("updated_at") if hasattr(StaffService, "updated_at") else None,
        ]
        cols = [c for c in cols if c is not None]

        stmt = (
            select(*cols)
            .select_from(StaffService)
            .join(Staff, Staff.id == StaffService.staff_id)
            .join(Service, Service.id == StaffService.service_id)
        )

        for c in where:
            stmt = stmt.where(c)

        if hasattr(StaffService, "created_at"):
            stmt = stmt.order_by(StaffService.created_at.desc())
        else:
            stmt = stmt.order_by(StaffService.id.desc())

        stmt = stmt.limit(limit).offset(offset)

        rows = (await self.db.execute(stmt)).mappings().all()
        return [dict(r) for r in rows], total
