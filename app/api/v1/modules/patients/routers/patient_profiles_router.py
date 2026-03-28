# app/api/v1/modules/patients/routers/patient_profiles_router.py
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.patients.dependencies import get_patient_profiles_service
from app.api.v1.modules.patients.services.patient_profiles_service_v2 import PatientProfilesService
from app.api.v1.modules.patients.models.patient_profiles_model import (
    PatientProfilePatch,
    PatientContactPatch,
    PatientMedicalFlagsPatch,
    PatientMarketingPatch,
)
from app.api.v1.modules.patients.models._envelopes.patient_profiles_envelopes import (
    PatientProfileGetEnvelope,
    PatientProfilePatchEnvelope,
    PatientContactGetEnvelope,
    PatientContactPatchEnvelope,
    PatientMedicalFlagsGetEnvelope,
    PatientMedicalFlagsPatchEnvelope,
    PatientMarketingGetEnvelope,
    PatientMarketingPatchEnvelope,
)

router = APIRouter()
# router = APIRouter(prefix="/patients", tags=["Patients"])


# =========================================================
# Profile
# =========================================================
@router.get(
    "/{patient_id:uuid}/profile",
    response_class=UnicodeJSONResponse,
    response_model=PatientProfileGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_profile",
)
async def read_profile(
    request: Request,
    patient_id: UUID = Path(..., description="patient id"),
    svc: PatientProfilesService = Depends(get_patient_profiles_service),
):
    data = await svc.get_profile(patient_id)
    if not data:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": data.model_dump()},
    )


@router.patch(
    "/{patient_id:uuid}/profile",
    response_class=UnicodeJSONResponse,
    response_model=PatientProfilePatchEnvelope,
    response_model_exclude_none=True,
    operation_id="patch_profile",
)
async def patch_profile(
    request: Request,
    patient_id: UUID,
    body: PatientProfilePatch,
    svc: PatientProfilesService = Depends(get_patient_profiles_service),
):
    data = await svc.patch_profile(patient_id, body)
    if not data:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": data.model_dump()},
    )


# =========================================================
# Contact
# =========================================================
@router.get(
    "/{patient_id:uuid}/contact",
    response_class=UnicodeJSONResponse,
    response_model=PatientContactGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_contact",
)
async def read_contact(
    request: Request,
    patient_id: UUID,
    svc: PatientProfilesService = Depends(get_patient_profiles_service),
):
    data = await svc.get_contact(patient_id)
    if not data:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": data.model_dump()},
    )


@router.patch(
    "/{patient_id:uuid}/contact",
    response_class=UnicodeJSONResponse,
    response_model=PatientContactPatchEnvelope,
    response_model_exclude_none=True,
    operation_id="patch_contact",
)
async def patch_contact(
    request: Request,
    patient_id: UUID,
    body: PatientContactPatch,
    svc: PatientProfilesService = Depends(get_patient_profiles_service),
):
    data = await svc.patch_contact(patient_id, body)
    if not data:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": data.model_dump()},
    )


# =========================================================
# Medical Flags
# =========================================================
@router.get(
    "/{patient_id:uuid}/medical-flags",
    response_class=UnicodeJSONResponse,
    response_model=PatientMedicalFlagsGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_medical_flags",
)
async def read_medical_flags(
    request: Request,
    patient_id: UUID,
    svc: PatientProfilesService = Depends(get_patient_profiles_service),
):
    data = await svc.get_medical_flags(patient_id)
    if not data:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": data.model_dump()},
    )


@router.patch(
    "/{patient_id:uuid}/medical-flags",
    response_class=UnicodeJSONResponse,
    response_model=PatientMedicalFlagsPatchEnvelope,
    response_model_exclude_none=True,
    operation_id="patch_medical_flags",
)
async def patch_medical_flags(
    request: Request,
    patient_id: UUID,
    body: PatientMedicalFlagsPatch,
    svc: PatientProfilesService = Depends(get_patient_profiles_service),
):
    data = await svc.patch_medical_flags(patient_id, body)
    if not data:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": data.model_dump()},
    )


# =========================================================
# Marketing
# =========================================================
@router.get(
    "/{patient_id:uuid}/marketing",
    response_class=UnicodeJSONResponse,
    response_model=PatientMarketingGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_marketing",
)
async def read_marketing(
    request: Request,
    patient_id: UUID,
    svc: PatientProfilesService = Depends(get_patient_profiles_service),
):
    data = await svc.get_marketing(patient_id)
    if not data:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": data.model_dump()},
    )


@router.patch(
    "/{patient_id:uuid}/marketing",
    response_class=UnicodeJSONResponse,
    response_model=PatientMarketingPatchEnvelope,
    response_model_exclude_none=True,
    operation_id="patch_marketing",
)
async def patch_marketing(
    request: Request,
    patient_id: UUID,
    body: PatientMarketingPatch,
    svc: PatientProfilesService = Depends(get_patient_profiles_service),
):
    data = await svc.patch_marketing(patient_id, body)
    if not data:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_404", "Resource not found."),
            details={"patient_id": str(patient_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": data.model_dump()},
    )
