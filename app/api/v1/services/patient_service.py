# app/api/v1/services/patient_service.py

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.patient import Patient
from app.api.v1.models.patient_model import PatientCreate, PatientUpdate, PatientRead


def _raise_integrity_error(e: IntegrityError) -> None:
    msg = str(getattr(e, "orig", e)).lower()
    if "ak_patients_email" in msg:
        raise ValueError("email already exists")
    if "ak_patients_id_card_no" in msg:
        raise ValueError("id_card_no already exists")
    if "ak_patients_code" in msg:
        raise ValueError("patient_code already exists")
    raise ValueError("duplicate key / integrity error")


def _to_read_dict(obj: Patient) -> dict:
    return PatientRead.model_validate(obj).model_dump()


def _with_refs(stmt):
    # โหลด relationship allergies/alerts (ไม่พังแม้ schema ยังไม่ส่ง nested)
    return stmt.options(
        selectinload(Patient.allergy),
        selectinload(Patient.drug_allergy),
        selectinload(Patient.alert),
    )


async def list_patients(db: AsyncSession, limit: int = 50, offset: int = 0) -> List[dict]:
    stmt = (
        _with_refs(select(Patient))
        .order_by(Patient.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    return [_to_read_dict(p) for p in res.scalars().all()]


async def get_patient(db: AsyncSession, patient_id: UUID) -> Optional[dict]:
    stmt = _with_refs(select(Patient)).where(Patient.id == patient_id)
    res = await db.execute(stmt)
    obj = res.scalars().first()
    return _to_read_dict(obj) if obj else None


async def search_patients(
    db: AsyncSession,
    q_text: str = "",
    status: str = "",
    limit: int = 50,
    offset: int = 0,
) -> List[dict]:
    stmt = _with_refs(select(Patient)).where(Patient.is_active.is_(True))

    if q_text:
        kw = f"%{q_text}%"
        stmt = stmt.where(
            or_(
                Patient.first_name_lo.ilike(kw),
                Patient.last_name_lo.ilike(kw),
                Patient.first_name_en.ilike(kw),
                Patient.last_name_en.ilike(kw),
                Patient.patient_code.ilike(kw),
                Patient.telephone.ilike(kw),
                Patient.id_card_no.ilike(kw),
            )
        )

    if status:
        stmt = stmt.where(Patient.status == status)

    stmt = stmt.order_by(Patient.created_at.desc()).limit(limit).offset(offset)
    res = await db.execute(stmt)
    return [_to_read_dict(p) for p in res.scalars().all()]



async def create_patient(db: AsyncSession, payload: PatientCreate) -> dict:
    obj = Patient(**payload.model_dump())

    db.add(obj)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        _raise_integrity_error(e)

    await db.refresh(obj)
    return _to_read_dict(obj)


async def patch_patient(db: AsyncSession, patient_id: UUID, payload: PatientUpdate) -> dict:
    obj = await db.get(Patient, patient_id)
    if not obj:
        raise ValueError("patient not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise ValueError("no fields to update")

    for k, v in updates.items():
        setattr(obj, k, v)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        _raise_integrity_error(e)

    await db.refresh(obj)
    return _to_read_dict(obj)


async def delete_patient(db: AsyncSession, patient_id: UUID) -> UUID:
    obj = await db.get(Patient, patient_id)
    if not obj:
        raise ValueError("patient not found")

    await db.delete(obj)
    await db.commit()
    return obj.id
