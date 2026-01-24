from app.core.config import get_settings
settings = get_settings()  # ✅ load settings

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.patients_model import PatientTypeCreate, PatientTypeUpdate
from app.api.v1.services.patients_service import (
    create_patient_type,
    get_all_patient_types,
    get_patient_type_by_id,
    update_patient_type_by_id,
    delete_patient_type_by_id,
)

router = APIRouter(
    prefix="/api/v1/patient_types",
    tags=["Patient_Settings"],
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_patient_type_by_id(
    patientType: PatientTypeCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await create_patient_type(db, patientType)
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patientType": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=UnicodeJSONResponse)
async def read_patient_type_by_all(
    db: AsyncSession = Depends(get_db),
):
    items = await get_all_patient_types(db)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(items), "patientType": items},
    )


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_patient_type_by_id(
    patient_type_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    item = await get_patient_type_by_id(db, patient_type_id)
    if item is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"patient_type_id": str(patient_type_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"patientType": item},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_patient_type(
    patient_type_id: UUID,
    patientType: PatientTypeUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await update_patient_type_by_id(db, patient_type_id, patientType)
        if obj is None:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"patient_type_id": str(patient_type_id)},
            )
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"patientType": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_patient_type(
    patient_type_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await delete_patient_type_by_id(db, patient_type_id)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"patient_type_id": str(patient_type_id)},
            )
        return ResponseHandler.success(
            message=f"Patient type with ID {patient_type_id} deleted.",
            data={"patient_type_id": str(patient_type_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
