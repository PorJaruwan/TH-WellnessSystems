# app/api/v1/patients/patient_addresses.py

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.db.models.patient_settings import PatientAddress
from app.api.v1.modules.patients.models.patients_model import PatientAddressCreate, PatientAddressUpdate, PatientAddressRead
from app.api.v1.modules.patients.models._envelopes.patient_addresses_envelopes import (
    PatientAddressSingleEnvelope,
    PatientAddressListEnvelope,
    PatientAddressDeleteEnvelope,
)

from app.api.v1.modules.patients.repositories.patient_addresses_repository import PatientAddressesRepository, DEFAULT_SORT_BY, DEFAULT_SORT_ORDER
from app.api.v1.modules.patients.services.patient_addresses_service_v2 import PatientAddressesService

def get_addresses_service(db: AsyncSession = Depends(get_db)) -> PatientAddressesService:
    # ✅ DI: repo -> service
    return PatientAddressesService(PatientAddressesRepository(db))

router = APIRouter()


DEFAULT_SORT_BY = "address_type"
DEFAULT_SORT_ORDER = "asc"
ALLOWED_SORT_FIELDS = {
    "address_type", "city", "state_province", "postal_code",
    "is_primary", "created_at", "updated_at",
}


@router.get(
    "/{patient_id:uuid}/addresses",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressListEnvelope,
    response_model_exclude_none=True,
)
async def search_patient_addresses(
    request: Request,
    patient_id: UUID = Path(..., description="patient id"),
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(default=None, description="search address text"),
    address_type: str = Query(default="", description="home/work/other etc."),
    is_primary: Optional[bool] = Query(default=None),

    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default=DEFAULT_SORT_ORDER, pattern="^(asc|desc)$"),

    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    try:
        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = DEFAULT_SORT_BY

        result = await svc.list(q=q or "", patient_id=patient_id, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)
        items = result["payload"].items
        total = result["total"]

        filters = {
            "q": q,
            "patient_id": str(patient_id),
            "address_type": address_type or None,
            "is_primary": is_primary,
        }

        if total == 0:
            return ResponseHandler.error_from_request(request, *("DATA_204", "No data found."), details={"filters": filters})

        typed = [PatientAddressRead.model_validate(x).model_dump() for x in items]

        return ResponseHandler.success_from_request(request, 
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={
                "filters": filters,
                "sort": {"by": sort_by, "order": sort_order},
                "paging": {"total": total, "limit": limit, "offset": offset},
                "items": typed,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{patient_id:uuid}/addresses/{address_type}",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressSingleEnvelope,
    response_model_exclude_none=True,
)
async def get_patient_address_by_key(
    request: Request,
    patient_id: UUID,
    address_type: str = Path(..., description="home/work/other etc."),
    db: AsyncSession = Depends(get_db),
):
    item = await get_patient_address(db, patient_id=patient_id, address_type=address_type)
    if item is None:
        return ResponseHandler.error_from_request(request, 
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id), "address_type": address_type},
        )
    return ResponseHandler.success_from_request(request, 
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": PatientAddressRead.model_validate(item).model_dump()},
    )


@router.post(
    "/{patient_id:uuid}/addresses",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressSingleEnvelope,
    response_model_exclude_none=True,
)
async def create_patient_address_endpoint(
    request: Request,
    payload: PatientAddressCreate,
    patient_id: UUID = Path(..., description="patient id"),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = payload.model_dump()
        # Ensure patient_id from path wins over body (if any)
        data["patient_id"] = patient_id
        obj = PatientAddress(**data)
        created = await create_patient_address(db, obj)
        return ResponseHandler.success_from_request(request, 
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"item": PatientAddressRead.model_validate(created).model_dump()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{patient_id:uuid}/addresses/{address_type}",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressSingleEnvelope,
    response_model_exclude_none=True,
)
async def update_patient_address_endpoint(
    request: Request,
    payload: PatientAddressUpdate,
    patient_id: UUID = Path(..., description="patient id"),
    address_type: str = Path(..., description="home/work/other etc."),
    db: AsyncSession = Depends(get_db),
):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        obj = await update_patient_address(
            db,
            patient_id=patient_id,
            address_type=address_type,
            updates=updates,
        )
        if obj is None:
            return ResponseHandler.error_from_request(request, 
                *("DATA_404", "Resource not found."),
                details={"patient_id": str(patient_id), "address_type": address_type},
            )

        return ResponseHandler.success_from_request(request, 
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"item": PatientAddressRead.model_validate(obj).model_dump()},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{patient_id:uuid}/addresses/{address_type}",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_patient_address_endpoint(
    request: Request,
    patient_id: UUID = Path(..., description="patient id"),
    address_type: str = Path(..., description="home/work/other etc."),
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await delete_patient_address(db, patient_id=patient_id, address_type=address_type)
        if not deleted:
            return ResponseHandler.error_from_request(request, 
                *("DATA_404", "Resource not found."),
                details={"patient_id": str(patient_id), "address_type": address_type},
            )
        return ResponseHandler.success_from_request(request, 
            message=ResponseCode.SUCCESS["DELETED"][1] if "DELETED" in ResponseCode.SUCCESS else "Deleted.",
            data={"patient_id": str(patient_id), "address_type": address_type},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
