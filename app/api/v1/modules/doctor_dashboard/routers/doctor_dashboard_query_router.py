from __future__ import annotations

import logging
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.models._envelopes.base_envelopes import EnvelopeMeta
from app.api.v1.modules.doctor_dashboard.dependencies.doctor_dashboard_dependency import (
    get_doctor_dashboard_query_service,
)

from app.api.v1.modules.doctor_dashboard.schemas.doctor_dashboard_query_envelope import (
    ErrorResponse,
    SuccessResponse,
)
from app.api.v1.modules.doctor_dashboard.schemas.doctor_dashboard_query_params import (
    DoctorDashboardInboxBookingByIdQueryParams,
    DoctorDashboardInboxQueryParams,
    DoctorDashboardInboxSummaryQueryParams,
)
from app.api.v1.modules.doctor_dashboard.schemas.doctor_dashboard_query_response import (
    DoctorDashboardInboxBookingDetailResponse,
    DoctorDashboardInboxListResponse,
    DoctorDashboardInboxSummaryResponse,
)
from app.api.v1.modules.doctor_dashboard.services.doctor_dashboard_query_service import (
    DoctorDashboardQueryService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/doctor-dashboard",
    tags=["Doctor Dashboard"],
)


@router.get(
    "/inbox",
    response_model=SuccessResponse[DoctorDashboardInboxListResponse],
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    status_code=status.HTTP_200_OK,
    summary="Search doctor dashboard inbox",
    operation_id="search_doctor_dashboard_inbox",
)
async def search_doctor_dashboard_inbox(
    q: Optional[str] = Query(default=None),
    company_code: Optional[str] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    building_id: Optional[UUID] = Query(default=None),
    room_id: Optional[UUID] = Query(default=None),
    patient_id: Optional[UUID] = Query(default=None),
    primary_person_id: Optional[UUID] = Query(default=None),
    booking_date: Optional[date] = Query(default=None),
    status_value: Optional[str] = Query(default=None, alias="status"),
    consultation_type: Optional[str] = Query(default=None),
    note_status: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="start_time"),
    sort_dir: str = Query(default="asc"),
    service: DoctorDashboardQueryService = Depends(get_doctor_dashboard_query_service),
):
    try:
        params = DoctorDashboardInboxQueryParams(
            q=q,
            company_code=company_code,
            location_id=location_id,
            building_id=building_id,
            room_id=room_id,
            patient_id=patient_id,
            primary_person_id=primary_person_id,
            booking_date=booking_date,
            status=status_value,
            consultation_type=consultation_type,
            note_status=note_status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

        data = await service.search_inbox(params=params)

        return SuccessResponse[DoctorDashboardInboxListResponse](
            status="success",
            status_code=status.HTTP_200_OK,
            message="Doctor dashboard inbox fetched successfully",
            data=data,
            meta=EnvelopeMeta(
                company_code=company_code,
                path="/api/v1/doctor-dashboard/inbox",
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Failed to search doctor dashboard inbox. "
            "company_code=%s booking_date=%s location_id=%s building_id=%s room_id=%s patient_id=%s primary_person_id=%s",
            company_code,
            booking_date,
            location_id,
            building_id,
            room_id,
            patient_id,
            primary_person_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch doctor dashboard inbox",
        ) from exc


@router.get(
    "/inbox/summary",
    response_model=SuccessResponse[DoctorDashboardInboxSummaryResponse],
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    status_code=status.HTTP_200_OK,
    summary="Get doctor dashboard inbox summary",
    operation_id="get_doctor_dashboard_inbox_summary",
)
async def get_doctor_dashboard_inbox_summary(
    company_code: Optional[str] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    building_id: Optional[UUID] = Query(default=None),
    room_id: Optional[UUID] = Query(default=None),
    primary_person_id: Optional[UUID] = Query(default=None),
    booking_date: Optional[date] = Query(default=None),
    service: DoctorDashboardQueryService = Depends(get_doctor_dashboard_query_service),
):
    try:
        params = DoctorDashboardInboxSummaryQueryParams(
            company_code=company_code,
            location_id=location_id,
            building_id=building_id,
            room_id=room_id,
            primary_person_id=primary_person_id,
            booking_date=booking_date,
        )

        data = await service.get_inbox_summary(params=params)

        return SuccessResponse[DoctorDashboardInboxSummaryResponse](
            status="success",
            status_code=status.HTTP_200_OK,
            message="Doctor dashboard inbox summary fetched successfully",
            data=data,
            meta=EnvelopeMeta(
                company_code=company_code,
                path="/api/v1/doctor-dashboard/inbox/summary",
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Failed to get doctor dashboard inbox summary. "
            "company_code=%s booking_date=%s location_id=%s building_id=%s room_id=%s primary_person_id=%s",
            company_code,
            booking_date,
            location_id,
            building_id,
            room_id,
            primary_person_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch doctor dashboard inbox summary",
        ) from exc


@router.get(
    "/inbox/{booking_id}",
    response_model=SuccessResponse[DoctorDashboardInboxBookingDetailResponse],
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    status_code=status.HTTP_200_OK,
    summary="Read doctor dashboard inbox booking by id",
    operation_id="read_doctor_dashboard_inbox_booking_by_id",
)
async def read_doctor_dashboard_inbox_booking_by_id(
    booking_id: UUID,
    company_code: Optional[str] = Query(default=None),
    service: DoctorDashboardQueryService = Depends(get_doctor_dashboard_query_service),
):
    try:
        params = DoctorDashboardInboxBookingByIdQueryParams(
            company_code=company_code,
        )

        data = await service.get_inbox_booking_by_id(
            booking_id=booking_id,
            params=params,
        )

        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor dashboard booking not found",
            )

        return SuccessResponse[DoctorDashboardInboxBookingDetailResponse](
            status="success",
            status_code=status.HTTP_200_OK,
            message="Doctor dashboard booking fetched successfully",
            data=data,
            meta=EnvelopeMeta(
                company_code=company_code,
                path=f"/api/v1/doctor-dashboard/inbox/{booking_id}",
            ),
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Failed to read doctor dashboard inbox booking by id. "
            "booking_id=%s company_code=%s",
            booking_id,
            company_code,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch doctor dashboard booking",
        ) from exc