# app/api/v1/settings/room_availabilities.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import RoomAvailabilityCreate, RoomAvailabilityUpdate
from app.api.v1.models.settings_response_model import RoomAvailabilityResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_room_availability,
    orm_get_room_availability_by_id,
    orm_update_room_availability_by_id,
    orm_delete_room_availability_by_id,
)

from app.db.models import RoomAvailability

from app.utils.router_helpers import (
    respond_one,
    respond_list_paged,
    run_or_500,
)

router = APIRouter(prefix="/api/v1/room_availabilities", tags=["Core_Settings"])


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_room_availability(
    payload: RoomAvailabilityCreate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await orm_create_room_availability(session, clean_create(payload))
        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={
                "room_availability": RoomAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)
            },
        )

    return await run_or_500(_work)


@router.get("/search", response_class=UnicodeJSONResponse)
async def search_room_availabilities(
    session: AsyncSession = Depends(get_db),
    room_id: Optional[UUID] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"room_id": str(room_id) if room_id else None}

    async def _work():
        where = []
        if room_id:
            where.append(RoomAvailability.room_id == room_id)

        count_stmt = select(func.count()).select_from(RoomAvailability)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = select(RoomAvailability)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(RoomAvailability.available_date.desc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="room_availabilities",
            model_cls=RoomAvailabilityResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_room_availability(
    room_availability_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await orm_get_room_availability_by_id(session, room_availability_id)
        return respond_one(
            obj=obj,
            key="room_availability",
            model_cls=RoomAvailabilityResponse,
            not_found_details={"room_availability_id": str(room_availability_id)},
        )

    return await run_or_500(_work)


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_room_availability(
    room_availability_id: UUID,
    payload: RoomAvailabilityUpdate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await orm_update_room_availability_by_id(
            session, room_availability_id, clean_update(payload)
        )
        return respond_one(
            obj=obj,
            key="room_availability",
            model_cls=RoomAvailabilityResponse,
            not_found_details={"room_availability_id": str(room_availability_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_room_availability(
    room_availability_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        ok = await orm_delete_room_availability_by_id(session, room_availability_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"room_availability_id": str(room_availability_id)},
            )

        return ResponseHandler.success(
            "Deleted successfully.",
            data={"room_availability_id": str(room_availability_id)},
        )

    return await run_or_500(_work)
