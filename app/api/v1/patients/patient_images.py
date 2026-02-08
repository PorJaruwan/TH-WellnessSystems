# app/api/v1/patients/patient_images_v2.py
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.patients_model import PatientImageCreate, PatientImageUpdate
from app.api.v1.models._envelopes.patient_images_envelopes_v2 import (
    PatientImageListEnvelopeV2,
    PatientImageCreateEnvelopeV2,
    PatientImageByIdEnvelopeV2,
    PatientImageUpdateEnvelopeV2,
    PatientImageDeleteEnvelopeV2,
)

from app.api.v1.services.patient_images_service import (
    list_patient_images_v2,
    create_patient_image_v2,
    get_patient_image_by_id_v2,
    update_patient_image_by_id_v2,
    delete_patient_image_by_id_v2,
)

router = APIRouter(
    prefix="/patients/v2/images",
    tags=["Patients_V2"],
)


@router.get(
    "",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageListEnvelopeV2,
    response_model_exclude_none=True,
)
async def list_images(
    q: str | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    image_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: str | None = Query(default="-created_at", description="e.g. -created_at, created_at, -updated_at, image_type"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_patient_images_v2(
        db=db,
        q=q or "",
        patient_id=patient_id,
        image_type=image_type or "",
        limit=limit,
        offset=offset,
        sort=sort or "-created_at",
    )

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={
            "filters": {
                "q": q,
                "patient_id": patient_id,
                "image_type": image_type,
            },
            "paging": {
                "total": total,
                "limit": limit,
                "offset": offset,
            },
            "items": items,
        },
    )


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageCreateEnvelopeV2,
    response_model_exclude_none=True,
)
async def create_image(payload: PatientImageCreate, db: AsyncSession = Depends(get_db)):
    try:
        obj = await create_patient_image_v2(db, payload)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patient_image": obj},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{image_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageByIdEnvelopeV2,
    response_model_exclude_none=True,
)
async def get_image(image_id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await get_patient_image_by_id_v2(db, image_id)
    if obj is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"image_id": str(image_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"patient_image": obj})


@router.put(
    "/{image_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageUpdateEnvelopeV2,
    response_model_exclude_none=True,
)
async def update_image(image_id: UUID, payload: PatientImageUpdate, db: AsyncSession = Depends(get_db)):
    try:
        obj = await update_patient_image_by_id_v2(db, image_id, payload)
        if obj is None:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"image_id": str(image_id)})
        return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"patient_image": obj})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{image_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageDeleteEnvelopeV2,
    response_model_exclude_none=True,
)
async def delete_image(image_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        ok = await delete_patient_image_by_id_v2(db, image_id)
        if not ok:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"image_id": str(image_id)})
        return ResponseHandler.success(
            message=f"patient image with image_id {image_id} deleted.",
            data={"image_id": image_id},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
