# app/api/v1/patients/patient_addresses.py

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.db.models.patient_settings import PatientAddress
from app.api.v1.models.patients_model import PatientAddressCreate, PatientAddressUpdate, PatientAddressRead
from app.api.v1.models._envelopes.patient_addresses_envelopes import (
    PatientAddressSingleEnvelope,
    PatientAddressListEnvelope,
    PatientAddressDeleteEnvelope,
)

from app.api.v1.services.patient_addresses_service import (
    list_patient_addresses,
    get_patient_address,
    create_patient_address,
    update_patient_address,
    delete_patient_address,
)

router = APIRouter(
    prefix="/patients",
    tags=["Patient_Profiles"],
)

DEFAULT_SORT_BY = "address_type"
DEFAULT_SORT_ORDER = "asc"
ALLOWED_SORT_FIELDS = {
    "address_type", "city", "state_province", "postal_code",
    "is_primary", "created_at", "updated_at",
}


@router.get(
    "/addresses/search",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressListEnvelope,
    response_model_exclude_none=True,
)
async def search_patient_addresses(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(default=None, description="search address text"),
    patient_id: Optional[UUID] = Query(default=None),
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

        items, total = await list_patient_addresses(
            db,
            q=q or "",
            patient_id=patient_id,
            address_type=address_type,
            is_primary=is_primary,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        filters = {
            "q": q,
            "patient_id": str(patient_id) if patient_id else None,
            "address_type": address_type or None,
            "is_primary": is_primary,
        }

        if total == 0:
            return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={"filters": filters})

        typed = [PatientAddressRead.model_validate(x).model_dump() for x in items]

        return ResponseHandler.success(
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
    patient_id: UUID,
    address_type: str = Path(..., description="home/work/other etc."),
    db: AsyncSession = Depends(get_db),
):
    item = await get_patient_address(db, patient_id=patient_id, address_type=address_type)
    if item is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"patient_id": str(patient_id), "address_type": address_type},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": PatientAddressRead.model_validate(item).model_dump()},
    )


@router.post(
    "/addresses",
    response_class=UnicodeJSONResponse,
    response_model=PatientAddressSingleEnvelope,
    response_model_exclude_none=True,
)
async def create_patient_address_endpoint(
    payload: PatientAddressCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = PatientAddress(**payload.model_dump())
        created = await create_patient_address(db, obj)
        return ResponseHandler.success(
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
    patient_id: UUID,
    address_type: str,
    payload: PatientAddressUpdate,
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
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"patient_id": str(patient_id), "address_type": address_type},
            )

        return ResponseHandler.success(
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
    patient_id: UUID,
    address_type: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await delete_patient_address(db, patient_id=patient_id, address_type=address_type)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"patient_id": str(patient_id), "address_type": address_type},
            )
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1] if "DELETED" in ResponseCode.SUCCESS else "Deleted.",
            data={"patient_id": str(patient_id), "address_type": address_type},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
