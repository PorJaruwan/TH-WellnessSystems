from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.models as db_models

StaffLocation = db_models.StaffLocation
Staff = db_models.Staff
Location = getattr(db_models, "Location", getattr(db_models, "Locations", None))


class StaffLocationsSearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        staff_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        if Location is None:
            raise RuntimeError("Location model not found in app.db.models (expected Location or Locations)")

        where = []
        if staff_id:
            where.append(StaffLocation.staff_id == staff_id)
        if location_id:
            where.append(StaffLocation.location_id == location_id)
        if hasattr(StaffLocation, "is_active"):
            where.append(StaffLocation.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffLocation)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await self.db.execute(count_stmt)).scalar_one() or 0)

        cols = [
            StaffLocation.id.label("id"),
            StaffLocation.staff_id.label("staff_id"),
            StaffLocation.location_id.label("location_id"),
            Staff.staff_name.label("staff_name"),
            Location.location_name.label("location_name"),
            getattr(StaffLocation, "work_days").label("work_days") if hasattr(StaffLocation, "work_days") else None,
            getattr(StaffLocation, "work_time_from").label("work_time_from") if hasattr(StaffLocation, "work_time_from") else None,
            getattr(StaffLocation, "work_time_to").label("work_time_to") if hasattr(StaffLocation, "work_time_to") else None,
            getattr(StaffLocation, "is_primary").label("is_primary") if hasattr(StaffLocation, "is_primary") else None,
            getattr(StaffLocation, "is_active").label("is_active") if hasattr(StaffLocation, "is_active") else None,
            getattr(StaffLocation, "created_at").label("created_at") if hasattr(StaffLocation, "created_at") else None,
            getattr(StaffLocation, "updated_at").label("updated_at") if hasattr(StaffLocation, "updated_at") else None,
        ]
        cols = [c for c in cols if c is not None]

        stmt = (
            select(*cols)
            .select_from(StaffLocation)
            .join(Staff, Staff.id == StaffLocation.staff_id)
            .join(Location, Location.id == StaffLocation.location_id)
        )

        for c in where:
            stmt = stmt.where(c)

        if hasattr(StaffLocation, "created_at"):
            stmt = stmt.order_by(StaffLocation.created_at.desc())
        else:
            stmt = stmt.order_by(StaffLocation.id.desc())

        stmt = stmt.limit(limit).offset(offset)

        rows = (await self.db.execute(stmt)).mappings().all()
        return [dict(r) for r in rows], total
