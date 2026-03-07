# app/api/v1/modules/patients/services/patient_profiles_service_v2.py
from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.api.v1.modules.patients.repositories.patient_profiles_repository import PatientProfilesRepository

# ✅ FIX: ใช้ชื่อที่มีจริงใน patient_profiles_model.py
from app.api.v1.modules.patients.models.patient_profiles_model import (
    PatientProfileDTO,
    PatientProfilePatch,
    PatientContactDTO,
    PatientContactPatch,
    PatientMedicalFlagsDTO,
    PatientMedicalFlagsPatch,
    PatientMarketingDTO,
    PatientMarketingPatch,
)


class PatientProfilesService:
    """
    Patient profiles (stored on Patient table) - safe patch with allowlist.

    ✅ Standard rule:
    - service layer คืน DTO (ไม่คืน ORM)
    - patch ใช้ model_dump(exclude_unset=True, exclude_none=True)
    """

    def __init__(self, repo: PatientProfilesRepository):
        self.repo = repo

    async def _get_or_none(self, patient_id: UUID):
        return await self.repo.get_patient(patient_id)

    # ---------------------------
    # Profile
    # ---------------------------
    async def get_profile(self, patient_id: UUID) -> Optional[PatientProfileDTO]:
        p = await self._get_or_none(patient_id)
        return PatientProfileDTO.model_validate(p) if p else None

    async def patch_profile(self, patient_id: UUID, body: PatientProfilePatch) -> Optional[PatientProfileDTO]:
        p = await self._get_or_none(patient_id)
        if not p:
            return None

        data = body.model_dump(exclude_unset=True, exclude_none=True)
        for k, v in data.items():
            setattr(p, k, v)

        p = await self.repo.save(p)
        return PatientProfileDTO.model_validate(p)

    # ---------------------------
    # Contact
    # ---------------------------
    async def get_contact(self, patient_id: UUID) -> Optional[PatientContactDTO]:
        p = await self._get_or_none(patient_id)
        return PatientContactDTO.model_validate(p) if p else None

    async def patch_contact(self, patient_id: UUID, body: PatientContactPatch) -> Optional[PatientContactDTO]:
        p = await self._get_or_none(patient_id)
        if not p:
            return None

        data = body.model_dump(exclude_unset=True, exclude_none=True)
        for k, v in data.items():
            setattr(p, k, v)

        p = await self.repo.save(p)
        return PatientContactDTO.model_validate(p)

    # ---------------------------
    # Medical Flags
    # ---------------------------
    async def get_medical_flags(self, patient_id: UUID) -> Optional[PatientMedicalFlagsDTO]:
        p = await self._get_or_none(patient_id)
        return PatientMedicalFlagsDTO.model_validate(p) if p else None

    async def patch_medical_flags(
        self, patient_id: UUID, body: PatientMedicalFlagsPatch
    ) -> Optional[PatientMedicalFlagsDTO]:
        p = await self._get_or_none(patient_id)
        if not p:
            return None

        data = body.model_dump(exclude_unset=True, exclude_none=True)
        for k, v in data.items():
            setattr(p, k, v)

        p = await self.repo.save(p)
        return PatientMedicalFlagsDTO.model_validate(p)

    # ---------------------------
    # Marketing
    # ---------------------------
    async def get_marketing(self, patient_id: UUID) -> Optional[PatientMarketingDTO]:
        p = await self._get_or_none(patient_id)
        return PatientMarketingDTO.model_validate(p) if p else None

    async def patch_marketing(self, patient_id: UUID, body: PatientMarketingPatch) -> Optional[PatientMarketingDTO]:
        p = await self._get_or_none(patient_id)
        if not p:
            return None

        data = body.model_dump(exclude_unset=True, exclude_none=True)
        for k, v in data.items():
            setattr(p, k, v)

        p = await self.repo.save(p)
        return PatientMarketingDTO.model_validate(p)