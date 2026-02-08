# app/api/v1/settings/room_availabilities.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import RoomAvailabilityCreate, RoomAvailabilityUpdate
from app.api.v1.models.settings_response_model import (
    RoomAvailabilityResponse,
    RoomAvailabilityCreateEnvelope,
    RoomAvailabilitySearchEnvelope,
    RoomAvailabilityGetEnvelope,
    RoomAvailabilityUpdateEnvelope,
    RoomAvailabilityDeleteEnvelope,
)
from app.api.v1.services.settings_orm_service import (
    orm_create_room_availability,
    orm_get_room_availability_by_id,
    orm_update_room_availability_by_id,
    orm_delete_room_availability_by_id,
)

from app.db.models import RoomAvailability

from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/room_availabilities",
    tags=["Core_Settings"],
)

@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilityCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"room_availability": {"id": "<id>"}})
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
async def create_room_availability(payload: RoomAvailabilityCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_create_room_availability(session, clean_create(payload))
        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"room_availability": RoomAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilitySearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    "filters": {"room_id": None},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "room_availabilities": [],
                },
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
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
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

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
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/{room_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilityGetEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"room_availability": {"id": "<id>"}})
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def read_room_availability(room_availability_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_get_room_availability_by_id(session, room_availability_id)
        return respond_one(
            obj=obj,
            key="room_availability",
            model_cls=RoomAvailabilityResponse,
            not_found_details={"room_availability_id": str(room_availability_id)},
        )

    return await run_or_500(_work)


@router.put(
    "/{room_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilityUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(message=ResponseCode.SUCCESS["UPDATED"][1], data={"room_availability": {"id": "<id>"}})
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_room_availability(
    room_availability_id: UUID,
    payload: RoomAvailabilityUpdate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        data = clean_update(payload)
        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "room_availability_id": str(room_availability_id)},
                status_code=422,
            )

        obj = await orm_update_room_availability_by_id(session, room_availability_id, data)
        return respond_one(
            obj=obj,
            key="room_availability",
            model_cls=RoomAvailabilityResponse,
            not_found_details={"room_availability_id": str(room_availability_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/{room_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilityDeleteEnvelope,
    responses={
        **success_200_example(
            example=success_example(message=ResponseCode.SUCCESS["DELETED"][1], data={"room_availability_id": "<id>"})
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_room_availability(room_availability_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        ok = await orm_delete_room_availability_by_id(session, room_availability_id)
        if not ok:
            # ✅ CHANGED: เลิกใช้ ApiResponse.err
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"room_availability_id": str(room_availability_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"room_availability_id": str(room_availability_id)},
        )

    return await run_or_500(_work)




# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
# from uuid import UUID
# from typing import Optional

# from app.database.session import get_db
# from app.utils.payload_cleaner import clean_create, clean_update
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import success_200_example, common_errors, success_example
# from app.api.v1.models.bookings_model import ErrorEnvelope
# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

# from app.api.v1.models.settings_model import RoomAvailabilityCreate, RoomAvailabilityUpdate
# from app.api.v1.models.settings_response_model import RoomAvailabilityResponse, RoomAvailabilityCreateEnvelope, RoomAvailabilitySearchEnvelope, RoomAvailabilityGetEnvelope, RoomAvailabilityUpdateEnvelope, RoomAvailabilityDeleteEnvelope
# from app.api.v1.services.settings_orm_service import (
#     orm_create_room_availability,
#     orm_get_room_availability_by_id,
#     orm_update_room_availability_by_id,
#     orm_delete_room_availability_by_id,
# )

# from app.db.models import RoomAvailability

# from app.utils.router_helpers import (
#     respond_one,
#     respond_list_paged,
#     run_or_500,
# )


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/room_availabilities",
#     tags=["Core_Settings"],
# )


# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=RoomAvailabilityCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Registered successfully.', data={'room_availability': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, include_500=True),
#     })
# async def create_room_availability(
#     payload: RoomAvailabilityCreate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_create_room_availability(session, clean_create(payload))
#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["REGISTERED"][1],
#             data={
#                 "room_availability": RoomAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)
#             },
#         )

#     return await run_or_500(_work)


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=RoomAvailabilitySearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'filters': {'q': ''}, 'paging': {'total': 0, 'limit': 50, 'offset': 0}, 'room_availabilities': []})),
#         **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
#     })
# async def search_room_availabilities(
#     session: AsyncSession = Depends(get_db),
#     room_id: Optional[UUID] = Query(default=None),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {"room_id": str(room_id) if room_id else None}

#     async def _work():
#         where = []
#         if room_id:
#             where.append(RoomAvailability.room_id == room_id)

#         count_stmt = select(func.count()).select_from(RoomAvailability)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         stmt = select(RoomAvailability)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(RoomAvailability.available_date.desc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return respond_list_paged(
#             items=items,
#             plural_key="room_availabilities",
#             model_cls=RoomAvailabilityResponse,
#             filters=filters,
#             total=int(total),
#             limit=limit,
#             offset=offset,
#         )

#     return await run_or_500(_work)


# @router.get(
#     "/{room_availability_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=RoomAvailabilityGetEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'room_availability': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def read_room_availability(
#     room_availability_id: UUID,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_get_room_availability_by_id(session, room_availability_id)
#         return respond_one(
#             obj=obj,
#             key="room_availability",
#             model_cls=RoomAvailabilityResponse,
#             not_found_details={"room_availability_id": str(room_availability_id)},
#         )

#     return await run_or_500(_work)


# @router.put(
#     "/{room_availability_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=RoomAvailabilityUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'room_availability': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def update_room_availability(
#     room_availability_id: UUID,
#     payload: RoomAvailabilityUpdate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_update_room_availability_by_id(
#             session, room_availability_id, clean_update(payload)
#         )
#         return respond_one(
#             obj=obj,
#             key="room_availability",
#             model_cls=RoomAvailabilityResponse,
#             not_found_details={"room_availability_id": str(room_availability_id)},
#             message=ResponseCode.SUCCESS["UPDATED"][1],
#         )

#     return await run_or_500(_work)


# @router.delete(
#     "/{room_availability_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=RoomAvailabilityDeleteEnvelope,
#     responses={
#         **success_200_example(example=success_example(message='Deleted successfully.', data={'room_availability_id': '<id>'})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def delete_room_availability(
#     room_availability_id: UUID,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         ok = await orm_delete_room_availability_by_id(session, room_availability_id)
#         if not ok:
#             return ApiResponse.err(data_key="NOT_FOUND", default_code="DATA_001", default_message="Data not found.", details={"room_availability_id": str(room_availability_id)}, status_code=404)

#         return ResponseHandler.success(
#             "Deleted successfully.",
#             data={"room_availability_id": str(room_availability_id)},
#         )

#     return await run_or_500(_work)
