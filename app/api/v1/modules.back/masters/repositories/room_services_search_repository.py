# app/api/v1/modules/masters/repositories/room_services_search_repository.py

from sqlalchemy import select
from app.db.models.core_settings import RoomService  # ปรับ path ให้ตรงของคุณ

class RoomServiceSearchRepository:
    def __init__(self, db):
        self.db = db

    async def search(self, q: str | None, limit: int, offset: int):
        stmt = (
            select(
                RoomService.id.label("id"),
                RoomService.room_id.label("room_id"),   # <-- ปรับชื่อจริง
                RoomService.service_id.label("service_id"),   # <-- ปรับชื่อจริง
                RoomService.is_default.label("is_default"),
                RoomService.is_active.label("is_active"),
                RoomService.created_at.label("created_at"),
                RoomService.updated_at.label("updated_at"),
            )
        )

        # ใส่ filter ตามของคุณ...
        stmt = stmt.limit(limit).offset(offset)

        rows = (await self.db.execute(stmt)).mappings().all()  # ✅ dict-like rows
        return rows
    
##--old    
# from __future__ import annotations

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.models import RoomService
# from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


# class RoomServiceSearchRepository(BaseSettingsSearchRepository):
#     def __init__(self, session: AsyncSession):
#         super().__init__(session=session, model=RoomService, search_fields=['service_name', 'service_name_en', 'room_service_name', 'room_service_code'])
