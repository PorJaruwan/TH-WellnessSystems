# app/api/v1/services/patient_crud_service.py

from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import or_, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.patient_settings import (
    Patient, PatientAddress, PatientImage, PatientPhoto,
    Alert, Allergy, Source, MarketingStaff, PatientType, Profession, SaleStaff,
)

from app.api.v1.models.patients_model import (
    PatientCreate, PatientUpdate, PatientRead,
    PatientAddressCreate, PatientAddressUpdate,
    PatientImageCreate, PatientImageUpdate,
    AlertCreate, AlertUpdate,
    AllergyCreate, AllergyUpdate,
    SourceCreate, SourceUpdate,
    MarketingStaffCreate, MarketingStaffUpdate,
    PatientTypeCreate, PatientTypeUpdate,
    ProfessionCreate, ProfessionUpdate,
    SaleStaffCreate, SaleStaffUpdate,
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


def _to_read_dict(obj: Patient) -> dict:
    return PatientRead.model_validate(obj).model_dump()


def _with_refs(stmt):
    # โหลด relationship allergies/alerts (ไม่พังแม้ schema ยังไม่ส่ง nested)
    return stmt.options(
        selectinload(Patient.allergy),
        selectinload(Patient.drug_allergy),
        selectinload(Patient.alert),
    )


async def list_patients(db: AsyncSession, limit: int = 50, offset: int = 0) -> Tuple[List[dict], int]:
    # total (ทั้งหมดจริง)
    total_stmt = select(func.count()).select_from(Patient)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    # items (หน้าเดียว)
    stmt = (
        _with_refs(select(Patient))
        .order_by(Patient.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    items = [_to_read_dict(p) for p in res.scalars().all()]
    return items, total


async def get_patient(db: AsyncSession, patient_id: UUID) -> Optional[dict]:
    stmt = _with_refs(select(Patient)).where(Patient.id == patient_id)
    res = await db.execute(stmt)
    obj = res.scalars().first()
    return _to_read_dict(obj) if obj else None



async def search_patients(
    db: AsyncSession,
    q_text: str = "",
    status: str = "",
    source_type: str = "",   # ✅ NEW
    is_active: Optional[bool] = True,
    limit: int = 50,
    offset: int = 0,
):
    filters = []
    if is_active is not None:
        filters.append(Patient.is_active.is_(is_active))

    if q_text:
        kw = f"%{q_text}%"
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

    # ✅ NEW: filter by sources.source_type
    if source_type:
        src_ids_subq = select(Source.id).where(Source.source_type == source_type)
        filters.append(
            or_(
                Patient.source_id.in_(src_ids_subq),
                Patient.market_source_id.in_(src_ids_subq),
            )
        )

    total_stmt = select(func.count()).select_from(Patient).where(*filters)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    stmt = (
        _with_refs(select(Patient))
        .where(*filters)
        .order_by(Patient.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    items = [_to_read_dict(p) for p in res.scalars().all()]
    return items, total


async def create_patient(db: AsyncSession, payload: PatientCreate) -> dict:
    #obj = Patient(**payload.model_dump())
    obj = Patient(**payload.model_dump(exclude_none=True))

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





# ==============================
# Patient Addresses
# ==============================

async def get_all_patient_addresses(db: AsyncSession) -> List[PatientAddress]:
    result = await db.execute(
        select(PatientAddress).order_by(
            PatientAddress.patient_id.desc(),
            PatientAddress.address_type,
        )
    )
    return list(result.scalars().all())


async def get_patient_address_by_id(
    db: AsyncSession,
    patient_id: UUID,
) -> List[PatientAddress]:
    """
    ตีความว่า 'id' จาก router = patient_id
    คืน list address ทั้งหมดของ patient นี้
    """
    result = await db.execute(
        select(PatientAddress).where(PatientAddress.patient_id == patient_id)
    )
    return list(result.scalars().all())


# ชื่อเดิมสำหรับ router เก่า (เผื่อยังมีใช้ที่อื่น)
async def get_patient_addresses_by_patient_id(
    db: AsyncSession,
    patient_id: UUID,
) -> List[PatientAddress]:
    return await get_patient_address_by_id(db, patient_id)


# ==============================
# Patient Addresses (helper: by patient_code + address_type)
# ==============================

async def get_patient_address_by_code_type(
    db: AsyncSession,
    patient_code: str,
    address_type: str,
) -> Tuple[Optional[UUID], Optional[PatientAddress]]:
    """
    เดิมเวอร์ชัน Supabase คืน (patient_id, addr_res)
    เวอร์ชัน ORM นี้จะคืน (patient_id, PatientAddress|None)
    """
    # หา patient_id จาก patient_code ก่อน
    result = await db.execute(
        select(Patient.id).where(Patient.patient_code == patient_code)
    )
    patient_id: Optional[UUID] = result.scalar_one_or_none()
    if patient_id is None:
        return None, None

    # ดึง address ตาม patient_id + address_type
    result_addr = await db.execute(
        select(PatientAddress).where(
            PatientAddress.patient_id == patient_id,
            PatientAddress.address_type == address_type,
        )
    )
    address: Optional[PatientAddress] = result_addr.scalar_one_or_none()

    return patient_id, address


async def get_patient_address_by_key(
    db: AsyncSession,
    patient_id: UUID,
    address_type: str,
) -> Optional[PatientAddress]:
    result = await db.execute(
        select(PatientAddress).where(
            PatientAddress.patient_id == patient_id,
            PatientAddress.address_type == address_type,
        )
    )
    return result.scalar_one_or_none()


async def create_patient_address(
    db: AsyncSession,
    data: PatientAddressCreate,
) -> PatientAddress:
    obj = PatientAddress(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_patient_address(
    db: AsyncSession,
    patient_id: UUID,
    address_type: str,
    data: PatientAddressUpdate,
) -> Optional[PatientAddress]:
    obj = await get_patient_address_by_key(db, patient_id, address_type)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_patient_address(
    db: AsyncSession,
    patient_id: UUID,
    address_type: str,
) -> bool:
    obj = await get_patient_address_by_key(db, patient_id, address_type)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True


# ==============================
# Wrappers ให้ตรงกับ routers: update_patient_address_by_id / delete_patient_address_by_id
# ==============================

async def update_patient_address_by_id(
    db: AsyncSession,
    patient_id: UUID,
    data: PatientAddressUpdate,
) -> Optional[List[PatientAddress]]:
    """
    Router ส่ง addressId มา 1 ค่า
    ที่นี่ตีความว่า = patient_id แล้วอัปเดตทุก address ของ patient นั้น
    (ถ้าภายหลังต้องใช้ key อื่น ค่อยปรับเพิ่ม)
    """
    addresses = await get_patient_address_by_id(db, patient_id)
    if not addresses:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for addr in addresses:
        for field, value in update_data.items():
            setattr(addr, field, value)

    await db.commit()

    # refresh ทีละตัว
    for addr in addresses:
        await db.refresh(addr)

    return addresses


async def delete_patient_address_by_id(
    db: AsyncSession,
    patient_id: UUID,
) -> bool:
    """
    ตีความเหมือนกัน: ลบทุก address ของ patient_id นี้
    """
    addresses = await get_patient_address_by_id(db, patient_id)
    if not addresses:
        return False

    for addr in addresses:
        await db.delete(addr)
    await db.commit()
    return True


# ==============================
# Patient Images
# ==============================

async def create_patient_image(
    db: AsyncSession,
    data: PatientImageCreate,
) -> PatientImage:
    obj = PatientImage(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_all_patient_images(db: AsyncSession) -> List[PatientImage]:
    result = await db.execute(
        select(PatientImage).order_by(PatientImage.patient_id.desc())
    )
    return list(result.scalars().all())


async def get_patient_image_by_id(
    db: AsyncSession,
    image_id: UUID,
) -> Optional[PatientImage]:
    result = await db.execute(
        select(PatientImage).where(PatientImage.id == image_id)
    )
    return result.scalar_one_or_none()


async def update_patient_image_by_id(
    db: AsyncSession,
    image_id: UUID,
    data: PatientImageUpdate,
) -> Optional[PatientImage]:
    obj = await get_patient_image_by_id(db, image_id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_patient_image_by_id(
    db: AsyncSession,
    image_id: UUID,
) -> bool:
    obj = await get_patient_image_by_id(db, image_id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True


# ==============================
# Patient Photo (profile photo 1:1)
# ==============================

async def get_patient_photo_by_patient_id(
    db: AsyncSession,
    patient_id: UUID,
) -> Optional[PatientPhoto]:
    result = await db.execute(
        select(PatientPhoto).where(PatientPhoto.patient_id == patient_id)
    )
    return result.scalar_one_or_none()

