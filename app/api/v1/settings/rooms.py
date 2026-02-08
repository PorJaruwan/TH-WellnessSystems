# # app/api/v1/settings/rooms.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload  # ✅ CHANGED
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope

from app.api.v1.models.settings_model import RoomCreate, RoomUpdate
from app.api.v1.models.settings_response_model import (
    RoomResponse,
    RoomCreateEnvelope,
    RoomSearchEnvelope,
    RoomGetEnvelope,
    RoomUpdateEnvelope,
    RoomDeleteEnvelope,
)

from app.api.v1.services.settings_orm_service import (
    orm_get_room_by_id_with_names,  # ✅ CHANGED
    orm_create_room,
    orm_get_room_by_id,
    orm_update_room_by_id,
    orm_delete_room_by_id,
)

from app.db.models import Room

from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500


router = APIRouter(
    prefix="/rooms",
    tags=["Core_Settings"],
)


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=RoomCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["REGISTERED"][1],
                data={"room": {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
async def create_room(payload: RoomCreate, session: AsyncSession = Depends(get_db)):
    """
    Create (baseline = patients)

    Policy:
    - create -> 200 success
    """
    async def _work():
        data = clean_create(payload.model_dump(exclude_none=True))
        obj = await orm_create_room(session, data)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"room": RoomResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=RoomSearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    "filters": {"q": "", "is_active": True},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "rooms": [],
                },
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
async def search_rooms(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): room_code / room_name"),
    location_id: Optional[UUID] = Query(default=None, description="filter by location_id"),
    building_id: Optional[UUID] = Query(default=None, description="filter by building_id"),
    room_type_id: Optional[UUID] = Query(default=None, description="filter by room_type_id"),  # ✅ CHANGED
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    """
    Search/List (baseline = patients)
    Response data shape:
    - {"filters": {...}, "paging": {"total": N, "limit": L, "offset": O}, "rooms": [...]}

    Policy:
    - total == 0 => 404 DATA.EMPTY (handled by respond_list_paged)
    """
    filters = {
        "q": q,
        "location_id": str(location_id) if location_id else None,
        "building_id": str(building_id) if building_id else None,
        "room_type_id": str(room_type_id) if room_type_id else None,  # ✅ CHANGED
        "is_active": is_active,
    }

    async def _work():
        where = [Room.is_active == is_active]

        if location_id:
            where.append(Room.location_id == location_id)

        if building_id:
            where.append(Room.building_id == building_id)

        if room_type_id:
            where.append(Room.room_type_id == room_type_id)  # ✅ CHANGED

        if q:
            like = f"%{q}%"
            where.append(or_(Room.room_code.ilike(like), Room.room_name.ilike(like)))

        count_stmt = select(func.count(Room.id))
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        # ✅ CHANGED: eager load location/building/room_type names
        stmt = (
            select(Room)
            .options(
                selectinload(Room.location),
                selectinload(Room.building),
                selectinload(Room.room_type),
            )
        )
        for c in where:  # ✅ keep filters applied (สำคัญมาก)
            stmt = stmt.where(c)

        stmt = stmt.order_by(Room.room_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="rooms",
            model_cls=RoomResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/{room_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomGetEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={"room": {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def read_room(room_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Get by id (baseline = patients)

    Policy:
    - not found => 404 DATA.NOT_FOUND
    """
    async def _work():
        obj = await orm_get_room_by_id_with_names(session, room_id)  # ✅ CHANGED
        return respond_one(
            obj=obj,
            key="room",
            model_cls=RoomResponse,
            not_found_details={"room_id": str(room_id)},
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
        )

    return await run_or_500(_work)


@router.patch(
    "/{room_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["UPDATED"][1],
                data={"room": {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_room(room_id: UUID, payload: RoomUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update (baseline = patients)

    Policy:
    - not found => 404 DATA.NOT_FOUND
    """
    async def _work():
        data = clean_update(payload.model_dump(exclude_none=True))
        obj = await orm_update_room_by_id(session, room_id, data)
        return respond_one(
            obj=obj,
            key="room",
            model_cls=RoomResponse,
            not_found_details={"room_id": str(room_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/{room_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomDeleteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["DELETED"][1],
                data={"room_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_room(room_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Delete (baseline = patients)

    Policy:
    - not found => 404 DATA.NOT_FOUND
    """
    async def _work():
        ok = await orm_delete_room_by_id(session, room_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"room_id": str(room_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"room_id": str(room_id)},
        )

    return await run_or_500(_work)
