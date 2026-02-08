# app/api/v1/bookings/bookings.py
# Refactor: centralized OpenAPI responses via **common_errors(...)
# Uses: app/utils/api_response.py (ApiResponse) + app/utils/openapi_responses.py (common_errors pack)

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.utils.openapi_responses import common_errors, success_200_example, success_example

from app.api.v1.models.bookings_model import (
    BookingCreate,
    BookingUpdate,
    BookingUpdateNote,
    BookingStatusActionBody,
    BookingCreateData,
    BookingUpdateNoteData,
    BookingHistoryData,
    BookingSearchEnvelope,
    BookingByIdEnvelope,
    BookingCreateEnvelope,
    BookingUpdateEnvelope,
    BookingUpdateNoteEnvelope,
    BookingStatusActionEnvelope,
    BookingHistoryEnvelope,
    BookingDeleteEnvelope,
    ErrorEnvelope,
)

from app.api.v1.services.bookings_service import (
    booking_status_action_service,
    create_booking_service,
    delete_booking_service,
    get_booking_detail_service,
    get_booking_history_service,
    search_bookings_service,
    update_booking_by_id_service,
)

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])


# ==========================================================
# Normalizers
# ==========================================================
def _normalize_list_item(row: dict) -> dict:
    """
    booking_grid_view often returns booking_id; our Pydantic models use id.
    Convert: booking_id -> id
    """
    if not isinstance(row, dict):
        return row

    rid = row.get("booking_id") or row.get("id")
    return {
        "id": rid,
        "booking_date": row.get("booking_date"),
        "start_time": row.get("start_time"),
        "end_time": row.get("end_time"),
        "status": row.get("status"),
        "room_name": row.get("room_name") or "",
        "patient_name": row.get("patient_name") or "",
        "doctor_name": row.get("doctor_name") or "",
        "service_name": row.get("service_name") or "",
    }


def _normalize_detail(row: dict) -> dict:
    """
    booking_grid_view detail may return booking_id; our Pydantic model uses id.
    Convert: booking_id -> id
    """
    if not isinstance(row, dict):
        return row

    rid = row.get("booking_id") or row.get("id")
    out = dict(row)
    out.pop("booking_id", None)
    out["id"] = rid
    return out


# ==========================================================
# POST /api/v1/bookings (Create)
# ==========================================================
@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=BookingCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message="Registered successfully.",
                data={"booking": {"id": "uuid"}},
            )
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            invalid={"detail": "INVALID:payload..."},
        ),
    },
)
async def create_booking(
    payload: BookingCreate,
    session: AsyncSession = Depends(get_db),
):
    try:
        created = await create_booking_service(payload)

        data = BookingCreateData(
            booking=created,
        ).model_dump(exclude_none=True)

        return ApiResponse.ok(
            success_key="REGISTERED",
            default_message="Registered successfully.",
            data=data,
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(
            e,
            details={"payload": payload.model_dump(exclude_none=True)},
        )


# ==========================================================
# GET /api/v1/bookings/search
# ==========================================================
@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=BookingSearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message="Data retrieved successfully.",
                data={
                    "total": 2,
                    "count": 2,
                    "limit": 50,
                    "offset": 0,
                    "filters": {
                        "q": "john",
                        "company_code": "WP",
                        "location_id": "de17f143-8e6d-4367-a4be-4b2f9194c610",
                        "booking_date": "2026-01-27",
                    },
                    "bookings": [
                        {
                            "id": "17661d4a-2f16-4c9f-956d-fb2e8014dcab",
                            "booking_date": "2026-01-27",
                            "start_time": "09:30:00",
                            "end_time": "10:00:00",
                            "status": "booked",
                            "room_name": "Room A",
                            "patient_name": "John Doe",
                            "doctor_name": "Dr. A",
                            "service_name": "Consult",
                        }
                    ],
                },
            )
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            empty={"filters": {}},
            invalid={"detail": "INVALID:..."},
        ),
    },
)
async def search_bookings(
    session: AsyncSession = Depends(get_db),
    q: str | None = Query(default=None, description="keyword (patient/doctor/service/room)"),
    company_code: str | None = Query(default=None),
    location_id: UUID | None = Query(default=None),
    booking_date: date | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {
        "q": q or "",
        "company_code": company_code or "",
        "location_id": str(location_id) if location_id else "",
        "booking_date": booking_date.isoformat() if booking_date else "",
    }

    try:
        total, rows = await search_bookings_service(
            q=q,
            company_code=company_code,
            location_id=location_id,
            booking_date=booking_date,
            limit=limit,
            offset=offset,
        )

        if int(total) == 0:
            return ApiResponse.err(
                data_key="EMPTY",
                default_code="DATA_002",
                default_message="Data empty.",
                details={"filters": filters},
                status_code=404,
            )

        normalized = [_normalize_list_item(r) for r in (rows or [])]

        return ApiResponse.ok(
            success_key="RETRIEVED",
            default_message="Retrieved successfully.",
            data={
                "total": int(total),
                "count": len(normalized),
                "limit": limit,
                "offset": offset,
                "filters": filters,
                "bookings": normalized,
            },
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"filters": filters})


# ==========================================================
# GET /api/v1/bookings/{booking_id}
# ==========================================================
@router.get(
    "/{booking_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BookingByIdEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message="Data retrieved successfully.",
                data={"booking": {"id": "b3759a3a-1095-4f02-a546-0a7532cbb8b5"}},
            )
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            not_found={"booking_id": "b3759a3a-1095-4f02-a546-0a7532cbb8b5"},
            invalid={"detail": "INVALID:..."},
        ),
    },
)
async def get_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    try:
        booking = await get_booking_detail_service(booking_id=booking_id)

        booking_dict = booking.model_dump(exclude_none=True) if hasattr(booking, "model_dump") else booking
        booking_dict = _normalize_detail(booking_dict)

        return ApiResponse.ok(
            success_key="RETRIEVED",
            default_message="Retrieved successfully.",
            data={"booking": booking_dict},
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"booking_id": str(booking_id)})


# ==========================================================
# PATCH /api/v1/bookings/{booking_id}
# ==========================================================
@router.patch(
    "/{booking_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BookingUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message="Data updated successfully.",
                data={"booking": {"id": "uuid", "status": "confirmed"}},
            )
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            not_found={"booking_id": "uuid"},
            invalid={"detail": "INVALID:payload..."},
        ),
    },
)
async def update_booking(
    booking_id: UUID,
    payload: BookingUpdate,
    session: AsyncSession = Depends(get_db),
):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return ApiResponse.err(
            data_key="INVALID",
            default_code="DATA_003",
            default_message="Invalid request.",
            details={"booking_id": str(booking_id), "detail": "No fields to update"},
            status_code=422,
        )

    try:
        updated = await update_booking_by_id_service(booking_id=booking_id, payload=updates)
        updated_data = updated.model_dump(exclude_none=True) if hasattr(updated, "model_dump") else updated

        return ApiResponse.ok(
            success_key="UPDATED",
            default_message="Updated successfully.",
            data={"booking": updated_data},
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"booking_id": str(booking_id), "payload": updates})


# ==========================================================
# DELETE /api/v1/bookings/{booking_id}
# ==========================================================
@router.delete(
    "/{booking_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BookingDeleteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message="Data deleted successfully.",
                data={"booking_id": "uuid"},
            )
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            not_found={"booking_id": "uuid"},
            invalid={"detail": "INVALID:..."},
        ),
    },
)
async def delete_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    try:
        await delete_booking_service(booking_id=booking_id)

        return ApiResponse.ok(
            success_key="DELETED",
            default_message="Deleted successfully.",
            data={"booking_id": str(booking_id)},
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"booking_id": str(booking_id)})


# ==========================================================
# PATCH /api/v1/bookings/{booking_id}/note
# ==========================================================
@router.patch(
    "/{booking_id:uuid}/note",
    response_class=UnicodeJSONResponse,
    response_model=BookingUpdateNoteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message="Data updated successfully.",
                data={"booking_id": "uuid"},
            )
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            not_found={"booking_id": "uuid"},
            invalid={"detail": "INVALID:payload..."},
        ),
    },
)
async def update_booking_note(
    booking_id: UUID,
    body: BookingUpdateNote,
    session: AsyncSession = Depends(get_db),
):
    try:
        await update_booking_by_id_service(booking_id=booking_id, payload={"note": body.note})

        data = BookingUpdateNoteData(
            booking_id=str(booking_id),
        ).model_dump(exclude_none=True)

        return ApiResponse.ok(
            success_key="UPDATED",
            default_message="Updated successfully.",
            data=data,
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"booking_id": str(booking_id), "note": body.note})


# ==========================================================
# POST /api/v1/bookings/{booking_id}/status
# ==========================================================
# @router.post(
#     "/{booking_id:uuid}/status",
#     response_class=UnicodeJSONResponse,
#     response_model=BookingStatusActionEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             example=success_example(
#                 message="Data updated successfully.",
#                 data={"result": {"booking_id": "uuid", "new_status": "confirmed"}},
#             )
#         ),
#         **common_errors(
#             error_model=ErrorEnvelope,
#             not_found={"booking_id": "uuid"},
#             invalid={"detail": "INVALID:action..."},
#         ),
#     },
# )
@router.post(
    "/{booking_id:uuid}/status",
    response_class=UnicodeJSONResponse,
    response_model=BookingStatusActionEnvelope,
    response_model_exclude_none=True,
    summary="Booking status action (confirm/checkin/start_service/complete/cancel/no_show/reschedule)",
    responses={
        **success_200_example(
            description=(
                "Success.\n\n"
                "Action meanings:\n"
                "- confirm: Confirm booking -> status=confirmed\n"
                "- checkin: Patient checked-in -> status=checked_in\n"
                "- start_service: Start service -> status=in_service\n"
                "- complete: Complete service -> status=completed\n"
                "- cancel: Cancel -> status=cancelled (requires cancel_reason)\n"
                "- no_show: Mark no-show -> status=no_show\n"
                "- reschedule: Reschedule -> status=rescheduled"
            ),
            example=success_example(
                message="Data updated successfully.",
                data={"result": {"booking_id": "uuid", "old_status": "draft", "status": "confirmed"}},
            ),
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            not_found={"booking_id": "uuid"},
            invalid={
                "detail": (
                    "INVALID:action must be one of "
                    "['cancel','checkin','complete','confirm','no_show','reschedule','start_service'] "
                    "or cancel_reason rules violated"
                )
            },
        ),
    },
)

async def booking_status_action(
    booking_id: UUID,
    payload: BookingStatusActionBody,
    session: AsyncSession = Depends(get_db),
):
    try:
        result = await booking_status_action_service(
            booking_id=booking_id,
            user_id=payload.user_id,
            action=payload.action,
            note=payload.note,
            cancel_reason=payload.cancel_reason,
            force=payload.force,
        )

        return ApiResponse.ok(
            success_key="UPDATED",
            default_message="Updated successfully.",
            data={"result": result},
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(
            e,
            details={"booking_id": str(booking_id), "action": payload.action},
        )


# ==========================================================
# GET /api/v1/bookings/{booking_id}/history
# ==========================================================
@router.get(
    "/{booking_id:uuid}/history",
    response_class=UnicodeJSONResponse,
    response_model=BookingHistoryEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message="Data retrieved successfully.",
                data={
                    "booking_id": "uuid",
                    "items": [
                        {
                            "id": "uuid",
                            "old_status": "draft",
                            "new_status": "confirmed",
                            "changed_at": "2026-01-27T15:10:56Z",
                            "changed_by": "uuid",
                            "note": "...",
                        }
                    ],
                },
            )
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            empty={"booking_id": "uuid"},
            invalid={"detail": "INVALID:..."},
        ),
    },
)
async def get_booking_history(
    booking_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    try:
        items = await get_booking_history_service(booking_id=booking_id)

        if not items:
            return ApiResponse.err(
                data_key="EMPTY",
                default_code="DATA_002",
                default_message="Data empty.",
                details={"booking_id": str(booking_id)},
                status_code=404,
            )

        out_items: list[dict] = []
        for it in items:
            out_items.append(it.model_dump(exclude_none=True) if hasattr(it, "model_dump") else it)

        data = BookingHistoryData(
            booking_id=str(booking_id),
            items=out_items,
        ).model_dump(exclude_none=True)

        return ApiResponse.ok(
            success_key="RETRIEVED",
            default_message="Retrieved successfully.",
            data=data,
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"booking_id": str(booking_id)})
