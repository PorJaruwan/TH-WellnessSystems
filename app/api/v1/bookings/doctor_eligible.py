from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date, time
from app.database.session import get_db
from app.api.v1.services.doctor_eligible_service import (
    DoctorSearchParams, 
    search_doctors_for_booking,)

router = APIRouter(
    prefix="/api/v1/doctors",
    tags=["Bookings"]
)

@router.get("/doctors-eligible")
async def check_doctors_eligible(
    room_id: UUID,
    role: str = "doctor",
    location_id: UUID | None = None,
    date: date | None = None,
    time: time | None = None,
    check_location: bool = False,
    check_timeslot: bool = False,
    check_booking: bool = False,
    db: AsyncSession = Depends(get_db),
):
    params = DoctorSearchParams(
        room_id=room_id,
        role=role,
        location_id=location_id,
        date=date,
        time=time,
        check_location=check_location,
        check_timeslot=check_timeslot,
        check_booking=check_booking,
    )
    return await search_doctors_for_booking(db, params)
