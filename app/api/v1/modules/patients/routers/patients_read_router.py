"""Patients Read Router (Detail)

✅ Separate from CRUD mutations to enforce clear query strategies:
- Search/List = projection-only (no ORM serialize)
- Read-by-id = explicit read service (can use ORM, but controlled)
- Mutations (POST/PATCH/DELETE) = CRUD service

✅ Response pattern:
- Always return ResponseHandler.success_from_request / error_from_request
  so meta (request_id/company_code/processing_ms/path) is consistent.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.patients.dependencies import get_patients_read_service
from app.api.v1.modules.patients.services.patients_read_service import PatientsReadService
from app.api.v1.modules.patients.models._envelopes.patients_profile_envelopes import PatientByIdEnvelope

router = APIRouter()


@router.get(
    "/{patient_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientByIdEnvelope,
    response_model_exclude_none=True,
    operation_id="read_patient",
)
async def read_patient(
    request: Request,
    patient_id: UUID,
    svc: PatientsReadService = Depends(get_patients_read_service),
):
    p = await svc.get_by_id(patient_id)
    if not p:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": p},
    )
