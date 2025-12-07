# app/api/booking_router.py
from datetime import date
from uuid import UUID
from pydantic import BaseModel                     # ✅ เพิ่มตรงนี้
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.services.supabase_client import supabase
from app.core.config import get_settings
from app.database.database import get_db          # ✅ ใช้สำหรับสร้าง AsyncSession
#from app.dependencies import get_current_user  # ถ้ามี

settings = get_settings()

from app.api.v1.models.bookings_model import (
    PatientListResponse,
    StaffListResponse,
    BuildingListResponse,
    RoomListResponse,
    BookingGridResponse,
    BookingCreate,
    BookingCreateResponse,
    BookingDetail,
    BookingUpdateNote,
    BookingHistoryResponse,
    BookingSearchResponse,
    AvailabilityResponse,
)
from app.api.v1.services.bookings_service import (
    search_patients_service,
    search_staff_service,
    get_buildings_service,
    get_rooms_service,
    get_booking_grid_service,
    create_booking_service,
    get_booking_detail_service,
    update_booking_note_service,
    checkin_booking_service,
    cancel_booking_service,
    get_booking_history_service,
    search_bookings_service,
    get_resource_availability_service,
)

router = APIRouter(
    prefix="/api/v1/bookings", 
    tags=["Bookings"]
)

# ---------- Lookup ----------
@router.get("/patients/search", response_model=PatientListResponse)
async def search_patients(
    patient_code: str | None = Query(
        None,
        description="Keyword for search (patient_code / name / telephone / email)",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),):
    #current_user: dict = Depends(get_current_user),  # ถ้าใช้ auth อยู่

    return await search_patients_service(
        db=db,
        patient_code=patient_code,  # 🔹 ส่งเข้าไปตรง ๆ ให้ service
        page=page,
        page_size=page_size,
    )


###
# @router.get("/patients", response_model=PatientListResponse)
# async def search_patients(
#     patient_code: str | None = Query(None, description="Search by patient code"),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1, le=100),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await search_patients_service(
#         db,
#         patient_code=patient_code or "",
#         page=page,
#         page_size=page_size,
#     )


@router.get("/staff", response_model=StaffListResponse)
async def search_staff(
    staff_name: str | None = Query(
        None,
        description="Filter by staff name (ILIKE search)"
    ),
    role: str | None = Query(
        None,
        description="Filter by staff role (exact match)"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await search_staff_service(
        db,
        staff_name=staff_name or "",
        role=role,
        page=page,
        page_size=page_size,
    )


@router.get("/buildings", response_model=BuildingListResponse)
async def get_buildings(
    location_id: UUID = Query(...),
    company_code: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await get_buildings_service(
        db,
        location_id=location_id,
        company_code=company_code,
    )


@router.get("/rooms", response_model=RoomListResponse)
async def get_rooms(
    building_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await get_rooms_service(db, building_id=building_id)


# ---------- Booking Grid ----------

@router.get("/booking-grid", response_model=BookingGridResponse)
async def get_booking_grid(
    date_: date = Query(..., alias="date"),
    company_code: str = Query(...),
    location_id: UUID = Query(...),
    building_id: UUID = Query(...),
    view_mode: str = Query("full", regex="^(full|am|pm)$"),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
):
    return await get_booking_grid_service(
        db,
        booking_date=date_,
        company_code=company_code,
        location_id=location_id,
        building_id=building_id,
        view_mode=view_mode,
        page=page,
    )


# ---------- Booking CRUD ----------

@router.post("/bookings", response_model=BookingCreateResponse)
async def create_booking(
    body: BookingCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_booking_service(db, body)


@router.get("/bookings/{booking_id}", response_model=BookingDetail)
async def get_booking_detail(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_booking_detail_service(db, booking_id=booking_id)


@router.patch("/bookings/{booking_id}")
async def update_booking_note(
    booking_id: UUID,
    body: BookingUpdateNote,
    db: AsyncSession = Depends(get_db),
):
    await update_booking_note_service(db, booking_id=booking_id, body=body)
    return {"id": booking_id, "status": "ok"}


# ---------- Status Actions ----------

@router.post("/bookings/{booking_id}/check-in")
async def checkin_booking(
    booking_id: UUID,
    note: str | None = Body(None),
    # TODO: เปลี่ยนเป็น current_user.id จาก auth จริง
    user_id: UUID = Body(..., embed=True, description="User performing check-in"),
    db: AsyncSession = Depends(get_db),
):
    return await checkin_booking_service(
        db,
        booking_id=booking_id,
        user_id=user_id,
        note=note,
    )


class CancelBody(BaseModel):
    reason: str | None = None
    note: str | None = None
    user_id: UUID


@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    body: CancelBody,
    db: AsyncSession = Depends(get_db),
):
    return await cancel_booking_service(
        db,
        booking_id=booking_id,
        user_id=body.user_id,
        reason=body.reason,
        note=body.note,
    )


@router.get("/bookings/{booking_id}/history", response_model=BookingHistoryResponse)
async def get_booking_history(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_booking_history_service(db, booking_id=booking_id)


# ---------- Search Bookings ----------
@router.get(
    "/bookings",
    response_model=BookingSearchResponse,
    summary="Search bookings by patient / doctor / service",
)
async def search_bookings(
    q: str | None = Query(
        None,
        description="Keyword (patient / doctor / service)",
    ),
    company_code: str | None = Query(
        None,
        description="Filter by company_code if needed",
    ),
    location_id: UUID | None = Query(
        None,
        description="Filter by location_id",
    ),
    booking_date: date | None = Query(
        None,
        description="Filter by booking_date",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await search_bookings_service(
        db,
        q=q,
        company_code=company_code,
        location_id=location_id,
        booking_date=booking_date,
        page=page,
        page_size=page_size,
    )

# ###
# @router.get("/bookings", response_model=BookingSearchResponse)
# async def search_bookings(
#     q: str | None = Query(None),
#     company_code: str | None = Query(None),
#     location_id: UUID | None = Query(None),
#     booking_date: date | None = Query(None),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1, le=100),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await search_bookings_service(
#         db,
#         q=q,
#         company_code=company_code,
#         location_id=location_id,
#         booking_date=booking_date,
#         page=page,
#         page_size=page_size,
#     )


# ---------- Availability ----------

@router.get("/availability/resource-tracks", response_model=AvailabilityResponse)
async def get_resource_availability(
    resource_track_id: UUID = Query(...),
    date_: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    return await get_resource_availability_service(
        db,
        resource_track_id=resource_track_id,
        date_=date_,
    )
