# app/api/v1/modules/masters/repositories/room_services_search_repository.py

from sqlalchemy import select, or_
from uuid import UUID
from app.db.models.core_settings import RoomService, Room, Service  # ✅ เพิ่ม Room, Service


class RoomServiceSearchRepository:
    def __init__(self, db):
        self.db = db

    
    async def search(
        self,
        q: str | None,
        room_id: UUID | None,
        service_id: UUID | None,
        is_active: bool | None,
        limit: int,
        offset: int,
        sort_by: str | None = None,
        sort_dir: str = "desc",
    ):
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
            .select_from(RoomService)
            .join(Room, RoomService.room_id == Room.id)
            .join(Service, RoomService.service_id == Service.id)
        )

        # keyword search: q -> room_name OR service_name
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Room.room_name.ilike(pattern),
                    Service.service_name.ilike(pattern),
                )
            )

        if room_id is not None:
            stmt = stmt.where(RoomService.room_id == room_id)

        if service_id is not None:
            stmt = stmt.where(RoomService.service_id == service_id)

        if is_active is not None:
            stmt = stmt.where(RoomService.is_active == is_active)

        # ordering (safe allow-list)
        sort_map = {
            "id": RoomService.id,
            "room_id": RoomService.room_id,
            "service_id": RoomService.service_id,
            "is_default": RoomService.is_default,
            "is_active": RoomService.is_active,
            "created_at": RoomService.created_at,
            "updated_at": RoomService.updated_at,
            "room_name": Room.room_name,
            "service_name": Service.service_name,
        }
        col = sort_map.get(sort_by or "")
        if col is not None:
            if (sort_dir or "").lower() == "asc":
                stmt = stmt.order_by(col.asc())
            else:
                stmt = stmt.order_by(col.desc())

        stmt = stmt.limit(limit).offset(offset)
        rows = (await self.db.execute(stmt)).mappings().all()
        return rows
    