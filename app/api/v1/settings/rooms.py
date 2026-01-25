# app/api/v1/settings/rooms.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.settings_model import RoomCreate, RoomUpdate
from app.api.v1.models.settings_response_model import RoomResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_room,
    orm_get_room_by_id,
    orm_update_room_by_id,
    orm_delete_room_by_id,
)

# ORM model สำหรับ search
from app.db.models import Room

# ✅ DRY helpers
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

router = APIRouter(
    prefix="/api/v1/rooms",
    tags=["Core_Settings"],
)


@router.post(
    "/create",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def create_room(payload: RoomCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_create_room(session, clean_create(payload))
        out = RoomResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"room": out},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def search_rooms(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): room_code / room_name"),
    location_id: Optional[UUID] = Query(default=None, description="filter by location_id"),
    building_id: Optional[UUID] = Query(default=None, description="filter by building_id"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    filters = {
        "q": q,
        "location_id": str(location_id) if location_id else None,
        "building_id": str(building_id) if building_id else None,
        "is_active": is_active,
    }

    async def _work():
        where = [Room.is_active == is_active]

        if location_id:
            where.append(Room.location_id == location_id)

        if building_id:
            where.append(Room.building_id == building_id)

        if q:
            kw = f"%{q}%"
            where.append(or_(Room.room_code.ilike(kw), Room.room_name.ilike(kw)))

        # ✅ total count (ตาม filter)
        count_stmt = select(func.count()).select_from(Room)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        # ✅ page query
        stmt = select(Room)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Room.room_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="rooms",
            model_cls=RoomResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_room(room_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_get_room_by_id(session, room_id)
        return respond_one(
            obj=obj,
            key="room",
            model_cls=RoomResponse,
            not_found_details={"room_id": str(room_id)},
        )

    return await run_or_500(_work)


@router.put(
    "/update-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def update_room(
    room_id: UUID,
    payload: RoomUpdate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await orm_update_room_by_id(session, room_id, clean_update(payload))
        return respond_one(
            obj=obj,
            key="room",
            model_cls=RoomResponse,
            not_found_details={"room_id": str(room_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_room(room_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        ok = await orm_delete_room_by_id(session, room_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"room_id": str(room_id)},
            )

        return ResponseHandler.success(
            message=f"Room with ID {room_id} deleted.",
            data={"room_id": str(room_id)},
        )

    return await run_or_500(_work)
