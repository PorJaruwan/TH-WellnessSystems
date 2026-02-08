# app/api/v1/bookings/bookings_staff.py

from app.core.config import get_settings
settings = get_settings()

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.bookings_staff_model import (
    BookingStaffCreateModel,
    BookingStaffUpdateModel,
)
from app.api.v1.services.bookings_staff_service import (
    create_booking_staff,
    get_all_booking_staff,
    get_booking_staff_by_id,
    update_booking_staff_by_id,
    delete_booking_staff_by_id,
    get_booking_staff_by_booking_id,
)

router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Bookings"],
)

# -------------------------------------------------------
# Collection (Optional: for admin/debug)
# GET /api/v1/bookings/staff
# -------------------------------------------------------
@router.get("/staff/search", response_class=UnicodeJSONResponse, summary="List booking staff (all)")
def list_booking_staff():
    res = get_all_booking_staff()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "booking_staff": res.data},
    )


# -------------------------------------------------------
# Create staff assignment under a booking
# POST /api/v1/bookings/{booking_id}/staff
# -------------------------------------------------------
@router.post(
    "/{booking_id}/staff",
    response_class=UnicodeJSONResponse,
    summary="Add staff to a booking",
)
def create_booking_staff_for_booking(booking_id: UUID, booking_staff: BookingStaffCreateModel):
    try:
        data = jsonable_encoder(booking_staff)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}

        # enforce booking_id from path (source of truth)
        cleaned_data["booking_id"] = str(booking_id)

        res = create_booking_staff(cleaned_data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"booking_staff": res.data[0]},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# List staff assignments of a booking (filter by role)
# GET /api/v1/bookings/{booking_id}/staff?role=doctor
# -------------------------------------------------------
@router.get(
    "/{booking_id}/staff",
    response_class=UnicodeJSONResponse,
    summary="Get booking staff by booking_id (optional filter by role)",
)
def read_booking_staff_by_booking_id(booking_id: UUID, role: str | None = None):
    try:
        res = get_booking_staff_by_booking_id(booking_id, role)

        if not res.data:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"booking_id": str(booking_id), "role": role},
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"booking_staff": res.data},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# Item operations on booking_staff record
# GET /api/v1/bookings/staff/{booking_staff_id}
# PUT /api/v1/bookings/staff/{booking_staff_id}
# DELETE /api/v1/bookings/staff/{booking_staff_id}
# -------------------------------------------------------
@router.get(
    "/staff/{booking_staff_id}",
    response_class=UnicodeJSONResponse,
    summary="Get booking_staff by id",
)
def read_booking_staff(booking_staff_id: UUID):
    res = get_booking_staff_by_id(booking_staff_id)
    if not res.data:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"booking_staff_id": str(booking_staff_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"booking_staff": res.data[0]},
    )


@router.put(
    "/staff/{booking_staff_id}",
    response_class=UnicodeJSONResponse,
    summary="Update booking_staff by id",
)
def update_booking_staff(booking_staff_id: UUID, booking_staff: BookingStaffUpdateModel):
    try:
        updated = {
            "booking_id": booking_staff.booking_id,  # can be kept, but usually not changed
            "staff_id": booking_staff.staff_id,
            "role": booking_staff.role,
            "is_primary": booking_staff.is_primary,
            "note": booking_staff.note,
            "is_active": booking_staff.is_active,
        }

        res = update_booking_staff_by_id(booking_staff_id, updated)
        if not res.data:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"booking_staff_id": str(booking_staff_id)},
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"booking_staff": res.data[0]},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/staff/{booking_staff_id}",
    response_class=UnicodeJSONResponse,
    summary="Delete booking_staff by id",
)
def delete_booking_staff(booking_staff_id: UUID):
    try:
        res = delete_booking_staff_by_id(booking_staff_id)
        if not res.data:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"booking_staff_id": str(booking_staff_id)},
            )

        return ResponseHandler.success(
            message=f"booking_staff with ID {booking_staff_id} deleted.",
            data={"booking_staff_id": str(booking_staff_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
