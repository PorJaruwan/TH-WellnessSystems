from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Staff
from app.utils.payload_cleaner import clean_create, clean_update


class StaffCrudRepository:
    """DB layer: create/update/delete only (no commit/rollback)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _only_model_columns(model_cls, data: dict) -> dict:
        return {k: v for k, v in data.items() if hasattr(model_cls, k)}

    async def create(self, payload_model) -> Staff:
        data = self._only_model_columns(Staff, clean_create(payload_model))
        obj = Staff(**data)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = self._utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = self._utc_now()
        if hasattr(obj, "is_active") and getattr(obj, "is_active", None) is None:
            obj.is_active = True

        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, staff_id: UUID, payload_model) -> Staff | None:
        obj = await self.db.get(Staff, staff_id)
        if not obj:
            return None

        data = self._only_model_columns(Staff, clean_update(payload_model))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = self._utc_now()

        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, staff_id: UUID) -> UUID:
        obj = await self.db.get(Staff, staff_id)
        if not obj:
            raise ValueError("staff not found")

        await self.db.delete(obj)
        await self.db.flush()
        return obj.id
    
