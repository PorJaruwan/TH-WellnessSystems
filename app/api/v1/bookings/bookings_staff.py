from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.bookings_model import BookingStaffCreateModel, BookingStaffUpdateModel
from app.api.v1.services.bookings_service import (
    create_booking_staff, get_all_booking_staff, get_booking_staff_by_id,
    update_booking_staff_by_id, delete_booking_staff_by_id,
    get_booking_staff_by_booking_id
)

router = APIRouter(
    prefix="/api/v1/booking_staff", 
    tags=["Bookings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_booking_staff_by_id(booking_staff: BookingStaffCreateModel):
    try:
        data = jsonable_encoder(booking_staff)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_booking_staff(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"booking_staff": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_booking_staff_by_all():
    res = get_all_booking_staff()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "booking_staff": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_booking_staff(booking_staff_id: UUID):
    res = get_booking_staff_by_id(booking_staff_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"booking_staff_id": str(booking_staff_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"booking_staff": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_booking_staff(bookingStaffId: UUID, booking_staff: BookingStaffUpdateModel):
    try:
        updated = {
            "booking_id": booking_staff.booking_id,
            "staff_id": booking_staff.staff_id,
            "role": booking_staff.role,
            "is_primary": booking_staff.is_primary,
            "note": booking_staff.note,
            "is_active": booking_staff.is_active,
        }
        res = update_booking_staff_by_id(bookingStaffId, updated)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"bookingStaffId": str(bookingStaffId)})
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"booking_staff": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_booking_staff(bookingStaffId: UUID):
    try:
        res = delete_booking_staff_by_id(bookingStaffId)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"bookingStaffId": str(bookingStaffId)})
        return ResponseHandler.success(
            message=f"booking_staff with ID {bookingStaffId} deleted.",
            data={"bookingStaffId": str(bookingStaffId)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# app/api/v1/bookings/booking_staff.py
@router.get("/search-by-booking-id")
def read_booking_staff_by_booking_id(bookingId: UUID, role: str | None = None):
    try:
        res = get_booking_staff_by_booking_id(bookingId, role)

        if not res.data:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"bookingId": str(bookingId), "role": role}
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"booking_staff": res.data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))