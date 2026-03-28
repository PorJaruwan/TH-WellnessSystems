from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import StaffLocation


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StaffLocationsCrudRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> StaffLocation:
        obj = StaffLocation(**payload)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()
        if hasattr(obj, "is_active") and getattr(obj, "is_active", None) is None:
            obj.is_active = True

        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, staff_location_id: UUID, payload: dict) -> StaffLocation | None:
        obj = await self.db.get(StaffLocation, staff_location_id)
        if not obj:
            return None

        for k, v in payload.items():
            if hasattr(obj, k):
                setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, staff_location_id: UUID) -> bool:
        obj = await self.db.get(StaffLocation, staff_location_id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.flush()
        return True

