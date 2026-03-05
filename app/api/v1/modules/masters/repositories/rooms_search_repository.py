from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from uuid import UUID

# from app.db.models import Room
from app.db.models.core_settings import Room, Location, Building, RoomType
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository

class RoomSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            model=Room,
            search_fields=["room_code", "room_name"],
        )

    async def search(
        self,
        q: str = "",
        location_id: UUID | None = None,
        building_id: UUID | None = None,
        room_type_id: UUID | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
          
        # ✅ base filters
        base_filters = []
        if location_id is not None:
            base_filters.append(Room.location_id == location_id)
        if building_id is not None:
            base_filters.append(Room.building_id == building_id)
        if room_type_id is not None:
            base_filters.append(Room.room_type_id == room_type_id)
        if is_active is not None:
            base_filters.append(Room.is_active == is_active)

        # ✅ select room columns + joined names
        cols = [
            Room.id.label("id"),
            Room.location_id.label("location_id"),
            Room.building_id.label("building_id"),
            Room.room_type_id.label("room_type_id"),
            Room.room_code.label("room_code"),
            Room.room_name.label("room_name"),
            Room.capacity.label("capacity"),
            Room.is_available.label("is_available"),
            Room.is_active.label("is_active"),
            Room.floor_number.label("floor_number"),
            Room.created_at.label("created_at"),
            Room.updated_at.label("updated_at"),
            Location.location_name.label("location_name"),
            Building.building_name.label("building_name"),
            RoomType.type_name.label("type_name"),
        ]

        stmt = (
            select(
                Room.id.label("id"),
                Room.room_code.label("code"),
                Room.room_name.label("name"),
                Room.capacity,
                Room.is_available,
                Room.is_active,
                Room.floor_number,
                Room.created_at,
                Room.updated_at,
                Room.location_id,
                Room.building_id,
                Room.room_type_id,

                Location.location_name.label("location_name"),
                Building.building_name.label("building_name"),
                RoomType.type_name.label("type_name"),
                # ✅ keep originals too (optional / backward compatible)
                Room.room_code.label("room_code"),
                Room.room_name.label("room_name"),
            )
            .select_from(Room)
            .join(Location, Room.location_id == Location.id)
            .join(Building, Room.building_id == Building.id)
            .join(RoomType, Room.room_type_id == RoomType.id)
        )

        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Room.room_name.ilike(pattern),
                    Room.room_code.ilike(pattern),
                    Location.location_name.ilike(pattern),
                    Building.building_name.ilike(pattern),
                    RoomType.type_name.ilike(pattern),
                )
            )

        if location_id:
            stmt = stmt.where(Room.location_id == location_id)

        if building_id:
            stmt = stmt.where(Room.building_id == building_id)

        if room_type_id:
            stmt = stmt.where(Room.room_type_id == room_type_id)

        if is_active is not None:
            stmt = stmt.where(Room.is_active == is_active)

        # ✅ sorting (มาตรฐาน grid/search)
        sort_map = {
            "id": Room.id,
            "code": Room.room_code,
            "name": Room.room_name,
            "room_code": Room.room_code,
            "room_name": Room.room_name,
            "location_id": Room.location_id,
            "building_id": Room.building_id,
            "floor_number": Room.floor_number,
            "capacity": Room.capacity,
            "is_available": Room.is_available,
            "is_active": Room.is_active,
            "created_at": Room.created_at,
            "updated_at": Room.updated_at,
            "location_name": Location.location_name,
            "building_name": Building.building_name,
            "type_name": RoomType.type_name,
        }

        # default sort
        if sort_by is None:
            for cand in ("updated_at", "created_at", "id"):
                if cand in sort_map:
                    sort_by = cand
                    break

        sort_col = sort_map.get(sort_by or "")
        if sort_col is not None:
            if (sort_dir or "").lower() == "desc":
                stmt = stmt.order_by(sort_col.desc())
            else:
                stmt = stmt.order_by(sort_col.asc())
            # tie-breaker
            if "id" in sort_map and (sort_by or "") != "id":
                stmt = stmt.order_by(sort_map["id"].asc())


        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        rows = (await self.session.execute(stmt)).mappings().all()

        return rows, total


