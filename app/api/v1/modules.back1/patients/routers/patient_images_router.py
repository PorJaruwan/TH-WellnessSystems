# app/api/v1/modules/patients/routers/patient_images_router.py
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.patients.dependencies import get_patient_images_service
from app.api.v1.modules.patients.services.patient_images_service_v2 import PatientImagesService
from app.api.v1.modules.patients.models.patients_model import PatientImageCreate, PatientImageUpdate
from app.api.v1.modules.patients.models._envelopes.patient_images_envelopes import (
    PatientImageListEnvelope,
    PatientImageCreateEnvelope,
    PatientImageByIdEnvelope,
    PatientImageUpdateEnvelope,
    PatientImageDeleteEnvelope,
)

router = APIRouter()
# router = APIRouter(prefix="/patients", tags=["Patients"])


def _parse_sort(sort: str | None, default_by: str, default_order: str) -> tuple[str, str]:
    """Parse sort string like '-created_at' into (sort_by, sort_order)."""
    if not sort:
        return default_by, default_order
    s = sort.strip()
    if s.startswith("-"):
        return s[1:], "desc"
    return s, "asc"


@router.get(
    "/{patient_id:uuid}/images",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageListEnvelope,
    response_model_exclude_none=True,
    operation_id="serch_images",
)
async def serch_images(
    request: Request,
    patient_id: UUID = Path(..., description="patient id"),
    q: str | None = Query(default=None),
    image_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: str | None = Query(default="-created_at", description="e.g. -created_at, created_at, -updated_at"),
    svc: PatientImagesService = Depends(get_patient_images_service),
):
    sort_by, sort_order = _parse_sort(sort, default_by="created_at", default_order="desc")
    result = await svc.list(
        q=q or "",
        patient_id=patient_id,
        image_type=image_type,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=result["payload"].model_dump(),
    )


@router.get(
    "/images/{image_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageByIdEnvelope,
    response_model_exclude_none=True,
    operation_id="read_image",
)
async def read_image(
    request: Request,
    image_id: UUID,
    svc: PatientImagesService = Depends(get_patient_images_service),
):
    obj = await svc.get(image_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"image_id": str(image_id)},
            status_code=404,
        )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": obj.model_dump()},
    )


@router.post(
    "/{patient_id:uuid}/images",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_image",
)
async def create_image(
    request: Request,
    patient_id: UUID,
    payload: PatientImageCreate,
    svc: PatientImagesService = Depends(get_patient_images_service),
):
    # ✅ Ensure patient_id from path is authoritative
    body = payload.model_copy(update={"patient_id": patient_id})
    created = await svc.create(body)

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": created.model_dump()},
        status_code=201,
    )


@router.patch(
    "/images/{image_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_image",
)
async def update_image(
    request: Request,
    image_id: UUID,
    payload: PatientImageUpdate,
    svc: PatientImagesService = Depends(get_patient_images_service),
):
    updated = await svc.update(image_id, payload)
    if not updated:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"image_id": str(image_id)},
            status_code=404,
        )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": updated.model_dump()},
    )


@router.delete(
    "/images/{image_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientImageDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_image",
)
async def delete_image(
    request: Request,
    image_id: UUID,
    svc: PatientImagesService = Depends(get_patient_images_service),
):
    ok = await svc.delete(image_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"image_id": str(image_id)},
            status_code=404,
        )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"item": {"deleted": True, "image_id": str(image_id)}},
    )
