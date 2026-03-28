
# app/api/v1/modules/patients/routers/patient_photos_router.py
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.patients.models._envelopes.patient_photos_envelopes import (
    PatientPhotoListEnvelope,
    PatientPhotoSingleEnvelope,
    PatientPhotoUploadEnvelope,
    PatientPhotoDeleteEnvelope,
)

from app.api.v1.modules.patients.repositories.patient_photos_repository import (
    PatientPhotosRepository,
    DEFAULT_SORT_BY,
    DEFAULT_SORT_ORDER,
    _ALLOWED_SORT_FIELDS,
)
from app.api.v1.modules.patients.services.patient_photos_service_v2 import PatientPhotosService

router = APIRouter()
# router = APIRouter(prefix="/patients/v1/photos", tags=["Patients"])


def get_photos_service(db: AsyncSession = Depends(get_db)) -> PatientPhotosService:
    # ✅ DI: repo -> service
    return PatientPhotosService(PatientPhotosRepository(db))


@router.get(
    "/photos/search",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoListEnvelope,
    response_model_exclude_none=True,
    summary="Search Patient Photos",
    operation_id="search_patient_photos",
)
async def search_patient_photos(
    request: Request,
    svc: PatientPhotosService = Depends(get_photos_service),
    q: Optional[str] = Query(default=None),
    patient_id: Optional[UUID] = Query(default=None),
    sort_by: str = Query(default=DEFAULT_SORT_BY),
    sort_order: str = Query(default=DEFAULT_SORT_ORDER, pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        # ✅ allowlist sort fields
        if sort_by not in _ALLOWED_SORT_FIELDS:
            sort_by = DEFAULT_SORT_BY

        result = await svc.list(
            q=q or "",
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        if result["total"] == 0:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_204", "No data found."),
                details={"filters": {"q": q, "patient_id": patient_id}},
                status_code=404,
            )

        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["LISTED"][1],
            data=result["payload"].model_dump(exclude_none=True),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/photos/{photo_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="read_photo",
)
async def read_photo(
    request: Request,
    photo_id: UUID,
    svc: PatientPhotosService = Depends(get_photos_service),
):
    obj = await svc.get(photo_id)
    if obj is None:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"photo_id": str(photo_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": obj.model_dump(exclude_none=True)},
    )


@router.get(
    "/{patient_id:uuid}/photos",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="search_photo_by_patient",
)
async def search_photo_by_patient(
    request: Request,
    patient_id: UUID,
    svc: PatientPhotosService = Depends(get_photos_service),
):
    obj = await svc.get_by_patient(patient_id)
    if obj is None:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["LISTED"][1],
        data={"item": obj.model_dump(exclude_none=True)},
    )


@router.post(
    "/photos/upload",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoUploadEnvelope,
    response_model_exclude_none=True,
    operation_id="upload_photo",
)
async def upload_photo(
    request: Request,
    patient_id: UUID = Form(...),
    file: UploadFile = File(...),
    svc: PatientPhotosService = Depends(get_photos_service),
):
    """Upload/replace patient photo:
    1) upload bytes to Supabase Storage
    2) insert row to PatientImage table
    """
    try:
        file_bytes = await file.read()
        item = await svc.upload(
            patient_id=patient_id,
            file_bytes=file_bytes,
            original_filename=file.filename or "photo.jpg",
            content_type=file.content_type or "application/octet-stream",
        )
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["CREATED"][1],
            data={"patient_id": patient_id, "file_url": item["file_path"], "photo_id": str(item["id"])},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/photos/{photo_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientPhotoDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_photo",
)
async def delete_photo(
    request: Request,
    photo_id: UUID,
    svc: PatientPhotosService = Depends(get_photos_service),
):
    try:
        ok = await svc.delete(photo_id)
        if not ok:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_404", "Resource not found."),
                details={"photo_id": str(photo_id)},
                status_code=404,
            )
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"deleted": True, "photo_id": str(photo_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
