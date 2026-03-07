from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.db.models import RoomAvailability, Room
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class RoomAvailabilitySearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=RoomAvailability, search_fields=['day_of_week', 'start_time', 'end_time'])

    async def search(
        self,
        q: str = "",
        room_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        stmt = (
            select(
                RoomAvailability.id.label("id"),
                RoomAvailability.room_id.label("room_id"),
                RoomAvailability.available_date.label("available_date"),
                RoomAvailability.start_time.label("start_time"),
                RoomAvailability.end_time.label("end_time"),
                RoomAvailability.created_at.label("created_at"),
                Room.room_name.label("room_name"),
            )
            .select_from(RoomAvailability)
            .join(Room, RoomAvailability.room_id == Room.id)
        )

        # optional q (ถ้าอยากค้นตาม room_name/date)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Room.room_name.ilike(pattern),
                    RoomAvailability.available_date.cast(str).ilike(pattern),
                )
            )

        if room_id is not None:
            stmt = stmt.where(RoomAvailability.room_id == room_id)

        # ✅ sorting (มาตรฐาน grid/search)
        sort_map = {
            "id": RoomAvailability.id,
            "room_id": RoomAvailability.room_id,
            "available_date": RoomAvailability.available_date,
            "start_time": RoomAvailability.start_time,
            "end_time": RoomAvailability.end_time,
            "created_at": RoomAvailability.created_at,
            "room_name": Room.room_name,
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

        rows = (await self.session.execute(stmt.limit(limit).offset(offset))).mappings().all()
        return rows, total
    