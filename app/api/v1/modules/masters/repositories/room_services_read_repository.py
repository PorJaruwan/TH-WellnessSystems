from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RoomService, Room, Service
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsReadRepository


class RoomServiceReadRepository(BaseSettingsReadRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=RoomService, pk_field="id")

    async def get(self, id):
        stmt = (
            select(
                RoomService.id.label("id"),
                RoomService.room_id.label("room_id"),
                RoomService.service_id.label("service_id"),
                RoomService.is_default.label("is_default"),
                RoomService.is_active.label("is_active"),
                RoomService.created_at.label("created_at"),
                RoomService.updated_at.label("updated_at"),
                Room.room_name.label("room_name"),
                Service.service_name.label("service_name"),
            )
            .join(Room, Room.id == RoomService.room_id)
            .join(Service, Service.id == RoomService.service_id)
            .where(RoomService.id == id)
        )

        row = (await self.session.execute(stmt)).mappings().first()
        return dict(row) if row else None