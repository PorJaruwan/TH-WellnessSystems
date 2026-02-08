# app/api/v1/patients/patient_profiles.py

from __future__ import annotations

from urllib.parse import unquote
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.patient_profiles_model import (
    PatientProfilePatch,
    PatientContactPatch,
    PatientMedicalFlagsPatch,
    PatientMarketingPatch,
)

from app.api.v1.models._envelopes.patient_profiles_envelopes import (
    PatientProfileGetEnvelope,
    PatientProfilePatchEnvelope,
    PatientContactGetEnvelope,
    PatientContactPatchEnvelope,
    PatientMedicalFlagsGetEnvelope,
    PatientMedicalFlagsPatchEnvelope,
    PatientMarketingGetEnvelope,
    PatientMarketingPatchEnvelope,
    PatientSearchEnvelope,
)

from app.api.v1.services.patient_profile_service import (
    get_profile, patch_profile,
    get_contact, patch_contact,
    get_medical_flags, patch_medical_flags,
    get_marketing, patch_marketing,
    search_light,
)


router = APIRouter(
    # ✅ ให้เหมือนกลุ่มเดิม: /api/v1 ใส่ที่ main.py ตอน include_router
    prefix="/patients",
    tags=["Patient_Profiles"],
)


# =========================================================
# PROFILE
# =========================================================

@router.get(
    "/{patient_id:uuid}/profile",
    response_class=UnicodeJSONResponse,
    response_model=PatientProfileGetEnvelope,
    response_model_exclude_none=True,
)
async def get_patient_profile(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    dto = await get_profile(db, patient_id)
    if dto is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"profile": dto},
    )


@router.patch(
    "/{patient_id:uuid}/profile",
    response_class=UnicodeJSONResponse,
    response_model=PatientProfilePatchEnvelope,
    response_model_exclude_none=True,
)
async def patch_patient_profile(patient_id: UUID, payload: PatientProfilePatch, db: AsyncSession = Depends(get_db)):
    try:
        dto = await patch_profile(db, patient_id, payload.model_dump(exclude_unset=True))
        if dto is None:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
        return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"profile": dto})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# CONTACT
# =========================================================

@router.get(
    "/{patient_id:uuid}/contact",
    response_class=UnicodeJSONResponse,
    response_model=PatientContactGetEnvelope,
    response_model_exclude_none=True,
)
async def get_patient_contact(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    dto = await get_contact(db, patient_id)
    if dto is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"contact": dto})


@router.patch(
    "/{patient_id:uuid}/contact",
    response_class=UnicodeJSONResponse,
    response_model=PatientContactPatchEnvelope,
    response_model_exclude_none=True,
)
async def patch_patient_contact(patient_id: UUID, payload: PatientContactPatch, db: AsyncSession = Depends(get_db)):
    try:
        dto = await patch_contact(db, patient_id, payload.model_dump(exclude_unset=True))
        if dto is None:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
        return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"contact": dto})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# MEDICAL FLAGS
# =========================================================

@router.get(
    "/{patient_id:uuid}/medical-flags",
    response_class=UnicodeJSONResponse,
    response_model=PatientMedicalFlagsGetEnvelope,
    response_model_exclude_none=True,
)
async def get_patient_medical_flags(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    dto = await get_medical_flags(db, patient_id)
    if dto is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"medical_flags": dto})


@router.patch(
    "/{patient_id:uuid}/medical-flags",
    response_class=UnicodeJSONResponse,
    response_model=PatientMedicalFlagsPatchEnvelope,
    response_model_exclude_none=True,
)
async def patch_patient_medical_flags(patient_id: UUID, payload: PatientMedicalFlagsPatch, db: AsyncSession = Depends(get_db)):
    try:
        dto = await patch_medical_flags(db, patient_id, payload.model_dump(exclude_unset=True))
        if dto is None:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
        return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"medical_flags": dto})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# MARKETING
# =========================================================

@router.get(
    "/{patient_id:uuid}/marketing",
    response_class=UnicodeJSONResponse,
    response_model=PatientMarketingGetEnvelope,
    response_model_exclude_none=True,
)
async def get_patient_marketing(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    dto = await get_marketing(db, patient_id)
    if dto is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"marketing": dto})


@router.patch(
    "/{patient_id:uuid}/marketing",
    response_class=UnicodeJSONResponse,
    response_model=PatientMarketingPatchEnvelope,
    response_model_exclude_none=True,
)
async def patch_patient_marketing(patient_id: UUID, payload: PatientMarketingPatch, db: AsyncSession = Depends(get_db)):
    try:
        dto = await patch_marketing(db, patient_id, payload.model_dump(exclude_unset=True))
        if dto is None:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_id": str(patient_id)})
        return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"marketing": dto})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

