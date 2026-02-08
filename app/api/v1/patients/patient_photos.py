# app/api/v1/patients/patient_photos.py
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models._envelopes.patient_photos_envelopes import (
    PatientPhotoListEnvelope,
    PatientPhotoSingleEnvelope,
    PatientPhotoUploadEnvelope,
    PatientPhotoDeleteEnvelope,
)
from app.api.v1.services.patient_photos_service import (
    list_patient_photos,
    get_patient_photo_by_id,
    get_patient_photo_by_patient_id,
    upload_or_replace_patient_photo,
    delete_patient_photo_by_id,
    SORT_MAP,
    DEFAULT_SORT_BY,
    DEFAULT_SORT_ORDER,
)

router = APIRouter(prefix="/patients/v2/photos", tags=["Patients_"])


@router.get(
    "",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoListEnvelope,
    response_model_exclude_none=True,
)
async def list_photos(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(default=None),
    patient_id: Optional[UUID] = Query(default=None),
    sort_by: str = Query(default=DEFAULT_SORT_BY),
    sort_order: str = Query(default=DEFAULT_SORT_ORDER, pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        if sort_by not in SORT_MAP:
            sort_by = DEFAULT_SORT_BY

        items, total = await list_patient_photos(
            db,
            q=q or "",
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        filters = {"q": q, "patient_id": patient_id}

        if total == 0:
            return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={"filters": filters})

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={
                "filters": filters,
                "sort": {"by": sort_by, "order": sort_order},
                "paging": {"total": total, "limit": limit, "offset": offset},
                "items": items,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{photo_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoSingleEnvelope,
    response_model_exclude_none=True,
)
async def get_photo_by_id(photo_id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await get_patient_photo_by_id(db, photo_id)
    if obj is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"photo_id": str(photo_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"item": obj})


@router.get(
    "/by-patient/{patient_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoSingleEnvelope,
    response_model_exclude_none=True,
)
async def get_photo_by_patient(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await get_patient_photo_by_patient_id(db, patient_id)
    if obj is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"item": obj})


@router.post(
    "/upload",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoUploadEnvelope,
    response_model_exclude_none=True,
)
async def upload_photo(
    patient_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        file_bytes = await file.read()
        item = await upload_or_replace_patient_photo(
            db,
            patient_id=patient_id,
            file_bytes=file_bytes,
            original_filename=file.filename or "photo.jpg",
            content_type=file.content_type,
        )
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patient_id": patient_id, "file_url": item["file_path"]},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{photo_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_photo(photo_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        ok = await delete_patient_photo_by_id(db, photo_id)
        if not ok:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"photo_id": str(photo_id)})
        return ResponseHandler.success(
            message="Deleted.",
            data={"photo_id": photo_id},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
