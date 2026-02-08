# app/api/v1/services/patient_profile_service.py

from __future__ import annotations

from typing import Optional, Dict, Any, Tuple, List
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models.patient_settings import Patient  # ✅ ใช้ ORM จริงของคุณ

from app.api.v1.models.patient_profiles_model import (
    PatientProfileDTO,
    PatientContactDTO,
    PatientMedicalFlagsDTO,
    PatientMarketingDTO,
    PatientSearchItemDTO,
)


def _raise_integrity_error(e: IntegrityError) -> None:
    msg = str(getattr(e, "orig", e)).lower()
    if "ak_patients_email" in msg:
        raise ValueError("email already exists")
    if "ak_patients_id_card_no" in msg:
        raise ValueError("id_card_no already exists")
    if "ak_patients_code" in msg:
        raise ValueError("patient_code already exists")
    raise ValueError("duplicate key / integrity error")


async def _get_patient_or_none(db: AsyncSession, patient_id: UUID) -> Optional[Patient]:
    res = await db.execute(select(Patient).where(Patient.id == patient_id))
    return res.scalars().first()


def _apply_updates(obj: Patient, updates: Dict[str, Any], allowed: set[str]) -> Dict[str, Any]:
    safe = {k: v for k, v in updates.items() if k in allowed}
    if not safe:
        raise ValueError("no fields to update")
    for k, v in safe.items():
        setattr(obj, k, v)
    return safe


# =========================================================
# PROFILE
# =========================================================

async def get_profile(db: AsyncSession, patient_id: UUID) -> Optional[PatientProfileDTO]:
    obj = await _get_patient_or_none(db, patient_id)
    if not obj:
        return None
    return PatientProfileDTO.model_validate(obj)


async def patch_profile(db: AsyncSession, patient_id: UUID, updates: Dict[str, Any]) -> Optional[PatientProfileDTO]:
    obj = await _get_patient_or_none(db, patient_id)
    if not obj:
        return None

    allowed = {
        "patient_code",
        "title_lo", "first_name_lo", "last_name_lo",
        "title_en", "first_name_en", "last_name_en",
        "sex", "birth_date", "id_card_no",
        "patient_type_id", "profession_id",
        "status", "is_active",
    }
    _apply_updates(obj, updates, allowed)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        _raise_integrity_error(e)

    await db.refresh(obj)
    return PatientProfileDTO.model_validate(obj)


# =========================================================
# CONTACT
# =========================================================

async def get_contact(db: AsyncSession, patient_id: UUID) -> Optional[PatientContactDTO]:
    obj = await _get_patient_or_none(db, patient_id)
    if not obj:
        return None
    return PatientContactDTO.model_validate(obj)


async def patch_contact(db: AsyncSession, patient_id: UUID, updates: Dict[str, Any]) -> Optional[PatientContactDTO]:
    obj = await _get_patient_or_none(db, patient_id)
    if not obj:
        return None

    allowed = {
        "email", "telephone", "work_phone",
        "line_id", "facebook", "whatsapp",
        "main_contact_method",
        "contact_first_name", "contact_last_name",
        "contact_phone1", "contact_phone2",
        "contact_relationship",
    }
    _apply_updates(obj, updates, allowed)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        _raise_integrity_error(e)

    await db.refresh(obj)
    return PatientContactDTO.model_validate(obj)


# =========================================================
# MEDICAL FLAGS
# =========================================================

async def get_medical_flags(db: AsyncSession, patient_id: UUID) -> Optional[PatientMedicalFlagsDTO]:
    obj = await _get_patient_or_none(db, patient_id)
    if not obj:
        return None
    return PatientMedicalFlagsDTO.model_validate(obj)


async def patch_medical_flags(db: AsyncSession, patient_id: UUID, updates: Dict[str, Any]) -> Optional[PatientMedicalFlagsDTO]:
    obj = await _get_patient_or_none(db, patient_id)
    if not obj:
        return None

    allowed = {
        "allergy_id", "drug_allergy_id", "allergy_note",
        "alert_id", "alert_note", "alert_level",
        "critical_medical_note",
    }
    _apply_updates(obj, updates, allowed)

    await db.commit()
    await db.refresh(obj)
    return PatientMedicalFlagsDTO.model_validate(obj)


# =========================================================
# MARKETING
# =========================================================

async def get_marketing(db: AsyncSession, patient_id: UUID) -> Optional[PatientMarketingDTO]:
    obj = await _get_patient_or_none(db, patient_id)
    if not obj:
        return None
    return PatientMarketingDTO.model_validate(obj)


async def patch_marketing(db: AsyncSession, patient_id: UUID, updates: Dict[str, Any]) -> Optional[PatientMarketingDTO]:
    obj = await _get_patient_or_none(db, patient_id)
    if not obj:
        return None

    allowed = {
        "source_id", "market_source_id",
        "referral_source_note", "market_source_note",
        "salesperson_id", "marketing_person_id",
    }
    _apply_updates(obj, updates, allowed)

    await db.commit()
    await db.refresh(obj)
    return PatientMarketingDTO.model_validate(obj)


# =========================================================
# SEARCH (light)
# =========================================================

async def search_light(
    db: AsyncSession,
    q: str = "",
    status: str = "",
    is_active: Optional[bool] = True,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[PatientSearchItemDTO], int]:
    filters = []

    if is_active is not None:
        filters.append(Patient.is_active.is_(is_active))

    if q:
        kw = f"%{q}%"
        filters.append(
            or_(
                Patient.first_name_lo.ilike(kw),
                Patient.last_name_lo.ilike(kw),
                func.coalesce(Patient.first_name_en, "").ilike(kw),
                func.coalesce(Patient.last_name_en, "").ilike(kw),
                Patient.patient_code.ilike(kw),
                func.coalesce(Patient.telephone, "").ilike(kw),
                Patient.id_card_no.ilike(kw),
            )
        )

    if status:
        filters.append(Patient.status == status)

    total_stmt = select(func.count()).select_from(Patient).where(*filters)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    stmt = (
        select(Patient)
        .where(*filters)
        .order_by(Patient.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    rows = res.scalars().all()

    items = [PatientSearchItemDTO.model_validate(p) for p in rows]
    return items, total
