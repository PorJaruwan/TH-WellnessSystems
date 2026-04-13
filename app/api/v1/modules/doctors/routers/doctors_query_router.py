from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.models._envelopes.base_envelopes import EnvelopeMeta
from app.api.v1.modules.doctors.dependencies.doctors_query_dependency import (
    get_doctors_query_service,
)
from app.api.v1.modules.doctors.schemas.doctors_query_envelope import (
    ErrorResponse,
    SuccessResponse,
)
from app.api.v1.modules.doctors.schemas.doctors_query_params import (
    DoctorByServiceQueryParams,
)
from app.api.v1.modules.doctors.schemas.doctors_query_response import (
    DoctorByServiceListResponse,
)
from app.api.v1.modules.doctors.services.doctors_query_service import (
    DoctorsQueryService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


@router.get(
    "/by-service",
    response_model=SuccessResponse[DoctorByServiceListResponse],
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    status_code=status.HTTP_200_OK,
    summary="Get doctors by service_id or service_code",
)
async def get_doctors_by_service(
    service_id: Optional[UUID] = Query(default=None),
    service_code: Optional[str] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    primary_only: bool = Query(default=False),
    company_code: Optional[str] = Query(default=None),
    service: DoctorsQueryService = Depends(get_doctors_query_service),
):
    try:
        params = DoctorByServiceQueryParams(
            service_id=service_id,
            service_code=service_code,
            location_id=location_id,
            primary_only=primary_only,
            company_code=company_code,
        )

        data = await service.get_doctors_by_service(params=params)

        return SuccessResponse[DoctorByServiceListResponse](
            status="success",
            status_code=status.HTTP_200_OK,
            message="Doctors fetched successfully",
            data=data,
            meta=EnvelopeMeta(
                company_code=company_code,
                path="/api/v1/doctors/by-service",
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
            "Failed to fetch doctors by service. "
            "service_id=%s service_code=%s location_id=%s primary_only=%s company_code=%s",
            service_id,
            service_code,
            location_id,
            primary_only,
            company_code,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch doctors by service",
        ) from exc