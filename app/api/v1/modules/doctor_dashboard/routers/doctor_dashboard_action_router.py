from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.doctor_dashboard.dependencies.doctor_dashboard_dependency import (
    get_doctor_dashboard_action_service,
)
from app.api.v1.modules.doctor_dashboard.schemas.doctor_dashboard_action_request import (
    DoctorDashboardAcceptBookingRequest,
    DoctorDashboardRejectBookingRequest,
    DoctorDashboardRescheduleBookingRequest,
    DoctorDashboardStartConsultationRequest,
    DoctorDashboardUpdateNoteStatusRequest,
)
from app.api.v1.modules.doctor_dashboard.schemas.doctor_dashboard_action_response import (
    DoctorDashboardActionResponse,
)
from app.database.session import get_db

router = APIRouter(
    prefix="/doctor-dashboard",
    tags=["Doctor Dashboard"],
)


@router.post(
    "/actions/accept",
    response_model=DoctorDashboardActionResponse,
    operation_id="accept_doctor_dashboard_booking",
    summary="Accept doctor dashboard booking",
)
async def accept_doctor_dashboard_booking(
    booking_id: UUID,
    request: DoctorDashboardAcceptBookingRequest,
    db: AsyncSession = Depends(get_db),
):
    service = get_doctor_dashboard_action_service(db)
    return await service.accept_booking(booking_id=booking_id, **request.model_dump())


@router.post(
    "/actions/reject",
    response_model=DoctorDashboardActionResponse,
    operation_id="reject_doctor_dashboard_booking",
    summary="Reject doctor dashboard booking",
)
async def reject_doctor_dashboard_booking(
    booking_id: UUID,
    request: DoctorDashboardRejectBookingRequest,
    db: AsyncSession = Depends(get_db),
):
    service = get_doctor_dashboard_action_service(db)
    return await service.reject_booking(booking_id=booking_id, **request.model_dump())


@router.post(
    "/actions/start",
    response_model=DoctorDashboardActionResponse,
    operation_id="start_doctor_dashboard_consultation",
    summary="Start doctor dashboard consultation",
)
async def start_doctor_dashboard_consultation(
    booking_id: UUID,
    request: DoctorDashboardStartConsultationRequest,
    db: AsyncSession = Depends(get_db),
):
    service = get_doctor_dashboard_action_service(db)
    return await service.start_consultation(
        booking_id=booking_id,
        **request.model_dump(),
    )


@router.post(
    "/actions/reschedule",
    response_model=DoctorDashboardActionResponse,
    operation_id="reschedule_doctor_dashboard_booking",
    summary="Reschedule doctor dashboard booking",
)
async def reschedule_doctor_dashboard_booking(
    booking_id: UUID,
    request: DoctorDashboardRescheduleBookingRequest,
    db: AsyncSession = Depends(get_db),
):
    service = get_doctor_dashboard_action_service(db)
    return await service.reschedule_booking(
        booking_id=booking_id,
        **request.model_dump(),
    )


@router.post(
    "/actions/update-note-status",
    response_model=DoctorDashboardActionResponse,
    operation_id="update_doctor_dashboard_note_status",
    summary="Update doctor dashboard note status",
)
async def update_doctor_dashboard_note_status(
    booking_id: UUID,
    request: DoctorDashboardUpdateNoteStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    service = get_doctor_dashboard_action_service(db)
    return await service.update_note_status(
        booking_id=booking_id,
        **request.model_dump(),
    )