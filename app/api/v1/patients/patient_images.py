from app.core.config import get_settings
settings = get_settings()  # ✅ load settings

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.patients_model import PatientImageCreate, PatientImageUpdate
from app.api.v1.services.patients_service import (
    create_patient_image,
    get_all_patient_images,
    get_patient_image_by_id,
    update_patient_image_by_id,
    delete_patient_image_by_id,
)

router = APIRouter(
    prefix="/api/v1/patient_images",
    tags=["Patient_Settings"],
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_patient_image_by_id(
    patient_image: PatientImageCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await create_patient_image(db, patient_image)
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patient_image": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_class=UnicodeJSONResponse)
async def read_patient_image_by_all(
    db: AsyncSession = Depends(get_db),
):
    items = await get_all_patient_images(db)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(items), "patientImage": items},
    )


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_patient_image_by_id(
    patient_image_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    item = await get_patient_image_by_id(db, patient_image_id)
    if item is None:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"patient_image_id": str(patient_image_id)},
        )
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"patientImage": item},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_patient_image_endpoint(
    id: UUID = Query(..., description="ID of the patient image record to update"),
    patientImage: PatientImageUpdate = ...,
    db: AsyncSession = Depends(get_db),
):
    try:
        obj = await update_patient_image_by_id(db, id, patientImage)
        if obj is None:
            raise HTTPException(status_code=404, detail="Update failed or ID not found.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"patientImage": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_patient_image_by_id_endpoint(
    imageId: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await delete_patient_image_by_id(db, imageId)
        if not deleted:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"imageId": str(imageId)},
            )
        return ResponseHandler.success(
            message=f"patient image with imageId {imageId} deleted.",
            data={"imageId": str(imageId)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
