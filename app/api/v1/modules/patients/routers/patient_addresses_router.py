# app/api/v1/modules/patients/routers/patient_addresses_router.py

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.patients.models.patients_model import (
    PatientAddressCreate,
    PatientAddressUpdate,
    PatientAddressRead,
)
from app.api.v1.modules.patients.models._envelopes.patient_addresses_envelopes import (
    PatientAddressSingleEnvelope,
    PatientAddressListEnvelope,
    PatientAddressDeleteEnvelope,
)

from app.api.v1.modules.patients.repositories.patient_addresses_repository import (
    PatientAddressesRepository,
    DEFAULT_SORT_BY,
    DEFAULT_SORT_ORDER,
    ALLOWED_SORT_FIELDS,
)
from app.api.v1.modules.patients.services.patient_addresses_service_v2 import PatientAddressesService


def get_addresses_service(db: AsyncSession = Depends(get_db)) -> PatientAddressesService:
    return PatientAddressesService(PatientAddressesRepository(db))


router = APIRouter()


@router.get(
    "/{patient_id:uuid}/addresses",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressListEnvelope,
    response_model_exclude_none=True,
    operation_id="search_patient_addresses",
)
async def search_patient_addresses(
    request: Request,
    patient_id: UUID = Path(..., description="patient id"),
    q: Optional[str] = Query(default=None, description="search address text"),
    address_type: Optional[str] = Query(default=None, description="home/work/other etc."),
    is_primary: Optional[bool] = Query(default=None),
    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default=DEFAULT_SORT_ORDER, pattern="^(asc|desc)$"),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    svc: PatientAddressesService = Depends(get_addresses_service),
):
    """
    FIX:
    - inject svc via Depends (previously `svc` was not defined -> 500)
    - pass filters to service
    """
    try:
        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = DEFAULT_SORT_BY

        result = await svc.list(
            q=q or "",
            patient_id=patient_id,
            address_type=address_type,
            is_primary=is_primary,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        payload = result["payload"]
        total = result["total"]

        if total == 0:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_204", "No data found."),
                details={"filters": payload.filters},
            )

        # payload.items are PatientAddressRead already
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["LISTED"][1],
            data=payload.model_dump(exclude_none=True),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{patient_id:uuid}/addresses/{address_type}",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="serch_patient_address_by_type",
)
async def serch_patient_address_by_type(
    request: Request,
    patient_id: UUID,
    address_type: str = Path(..., description="home/work/other etc."),
    svc: PatientAddressesService = Depends(get_addresses_service),
):
    try:
        item = await svc.get_by_key(patient_id=patient_id, address_type=address_type)
        if item is None:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_404", "Resource not found."),
                details={"patient_id": str(patient_id), "address_type": address_type},
            )
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["LISTED"][1],
            data={"item": item.model_dump(exclude_none=True)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{patient_id:uuid}/addresses",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="create_patient_address",
)
async def create_patient_address(
    request: Request,
    payload: PatientAddressCreate,
    patient_id: UUID = Path(..., description="patient id"),
    svc: PatientAddressesService = Depends(get_addresses_service),
):
    try:
        data = payload.model_dump()
        data["patient_id"] = patient_id  # path wins
        created = await svc.create(PatientAddressCreate(**data))
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["CREATED"][1],
            data={"item": created.model_dump(exclude_none=True)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{patient_id:uuid}/addresses/{address_type}",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="update_patient_address",
)
async def update_patient_address(
    request: Request,
    payload: PatientAddressUpdate,
    patient_id: UUID = Path(..., description="patient id"),
    address_type: str = Path(..., description="home/work/other etc."),
    svc: PatientAddressesService = Depends(get_addresses_service),
):
    try:
        updated = await svc.update_by_key(
            patient_id=patient_id,
            address_type=address_type,
            body=payload,
        )
        if updated is None:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_404", "Resource not found."),
                details={"patient_id": str(patient_id), "address_type": address_type},
            )
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"item": updated.model_dump(exclude_none=True)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{patient_id:uuid}/addresses/{address_type}",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_patient_address",
)
async def delete_patient_address(
    request: Request,
    patient_id: UUID = Path(..., description="patient id"),
    address_type: str = Path(..., description="home/work/other etc."),
    svc: PatientAddressesService = Depends(get_addresses_service),
):
    try:
        deleted = await svc.delete_by_key(patient_id=patient_id, address_type=address_type)
        if not deleted:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_404", "Resource not found."),
                details={"patient_id": str(patient_id), "address_type": address_type},
            )
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["DELETED"][1] if "DELETED" in ResponseCode.SUCCESS else "Deleted.",
            data={"patient_id": str(patient_id), "address_type": address_type},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))