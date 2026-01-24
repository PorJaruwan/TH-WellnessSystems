from app.core.config import get_settings
settings = get_settings()  # ✅ load settings

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.patients_model import PatientAddressCreate, PatientAddressUpdate
from app.api.v1.services.patients_service import (
    get_all_patient_addresses,
    get_patient_address_by_id,
    get_patient_addresses_by_patient_id,
    get_patient_address_by_code_type,
    create_patient_address,
    update_patient_address_by_id,
    delete_patient_address_by_id,
)

router = APIRouter(
    prefix="/api/v1/patient_addresses",
    tags=["Patient_Settings"],
)


# ✅ READ ALL
@router.get("/search", response_class=UnicodeJSONResponse)
async def read_patient_address_by_all(
    db: AsyncSession = Depends(get_db),
):
    items = await get_all_patient_addresses(db)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(items), "patient_addresses": items},
    )


# ✅ READ BY addr_id
@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_patient_address_by_id_endpoint(
    addr_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    item = await get_patient_address_by_id(db, addr_id)
    if item is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"addr_id": str(addr_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"patient_addresses": item},
    )


# ✅ READ BY patient_id
@router.get("/search-by-patient-id", response_class=UnicodeJSONResponse)
async def read_patient_addresses_by_patient_id(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    items = await get_patient_addresses_by_patient_id(db, patient_id)
    if not items:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"patient_id": str(patient_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"patient_addresses": items},
    )


# ✅ READ BY patient_code + address_type
@router.get("/search-by-code-type", response_class=UnicodeJSONResponse)
async def get_patient_address_by_patientCode_and_patientType(
    patient_code: str,
    address_type: str,
    db: AsyncSession = Depends(get_db),
):
    patient_id, address = await get_patient_address_by_code_type(
        db,
        patient_code=patient_code,
        address_type=address_type,
    )
    if not patient_id:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"patient_code": patient_code},
        )
    if address is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"patient_code": patient_code, "address_type": address_type},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={
            "patient_code": patient_code,
            "address_type": address_type,
            "patient_address": address,
        },
    )


# ✅ CREATE
@router.post("/create", response_class=UnicodeJSONResponse)
async def create_patient_address_by_id(
    addresses: PatientAddressCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await create_patient_address(db, addresses)
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"addresses": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ UPDATE BY addr_id
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_patient_address_by_id_endpoint(
    addressId: UUID,
    addresses: PatientAddressUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await update_patient_address_by_id(db, addressId, addresses)
        if obj is None:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"addressId": str(addressId)},
            )
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"addresses": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ DELETE BY addrId
@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_patient_address_by_id_endpoint(
    addrId: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await delete_patient_address_by_id(db, addrId)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"addrId": str(addrId)},
            )
        return ResponseHandler.success(
            message=f"addresses with addrId {addrId} deleted.",
            data={"addrId": str(addrId)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
