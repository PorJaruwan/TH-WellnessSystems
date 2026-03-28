"""Patients CRUD Router (Mutations only)

✅ Why mutations-only?
- Keep query strategies separated:
  - Search/List: projection-only (patients_search_router.py)
  - Read-by-id: detail router (patients_read_router.py)
  - Mutations: create/update/delete (this file)

✅ Response pattern:
- Always return ResponseHandler.success_from_request / error_from_request
  so meta (request_id/company_code/processing_ms/path) is consistent.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.patients.dependencies import get_patients_crud_service
from app.api.v1.modules.patients.models.schemas import PatientCreate, PatientUpdate
from app.api.v1.modules.patients.models._envelopes.patients_crud_envelopes_v2 import (
    PatientCreateEnvelopeV2,
    PatientUpdateEnvelopeV2,
    PatientDeleteEnvelopeV2,
)
from app.api.v1.modules.patients.services.patients_crud_service import PatientsCrudService

router = APIRouter()
# router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=PatientCreateEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="create_patient",
)
async def create_patient(
    request: Request,
    payload: PatientCreate,
    svc: PatientsCrudService = Depends(get_patients_crud_service),
):
    """Create patient."""
    try:
        created = await svc.create(payload)
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["CREATED"][1],
            data={"item": created},
            status_code=201,
        )
    except ValueError as e:
        # Typically: unique constraint/integrity error mapped by service
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATABASE["DUPLICATE_ENTRY"],
            details={"error": str(e)},
            status_code=409,
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )


@router.patch(
    "/{patient_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientUpdateEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="patch_patient_",
)
async def patch_patient_(
    request: Request,
    patient_id: UUID,
    payload: PatientUpdate,
    svc: PatientsCrudService = Depends(get_patients_crud_service),
):
    """Update patient by id."""
    try:
        updated = await svc.patch(patient_id, payload)
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"item": updated},
        )
    except ValueError as e:
        msg = str(e).lower()
        if "not found" in msg:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_404", "Resource not found."),
                details={"patient_id": str(patient_id), "error": str(e)},
                status_code=404,
            )
        if "exists" in msg or "duplicate" in msg:
            return ResponseHandler.error_from_request(
                request,
                *ResponseCode.DATABASE["DUPLICATE_ENTRY"],
                details={"patient_id": str(patient_id), "error": str(e)},
                status_code=409,
            )
        return ResponseHandler.error_from_request(
            request,
            *("DATA_400", "Invalid request."),
            details={"patient_id": str(patient_id), "error": str(e)},
            status_code=400,
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )


@router.delete(
    "/{patient_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientDeleteEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="delete_patient",
)
async def delete_patient(
    request: Request,
    patient_id: UUID,
    svc: PatientsCrudService = Depends(get_patients_crud_service),
):
    """Delete patient by id."""
    try:
        deleted = await svc.delete(patient_id)
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"item": deleted},
        )
    except ValueError as e:
        msg = str(e).lower()
        if "not found" in msg:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_404", "Resource not found."),
                details={"patient_id": str(patient_id), "error": str(e)},
                status_code=404,
            )
        return ResponseHandler.error_from_request(
            request,
            *("DATA_400", "Invalid request."),
            details={"patient_id": str(patient_id), "error": str(e)},
            status_code=400,
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )
