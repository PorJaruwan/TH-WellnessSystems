# app/api/v1/services/patient_masters_service.py
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



# def _raise_integrity_error(e: IntegrityError) -> None:
#     msg = str(getattr(e, "orig", e)).lower()
#     if "ak_patients_email" in msg:
#         raise ValueError("email already exists")
#     if "ak_patients_id_card_no" in msg:
#         raise ValueError("id_card_no already exists")
#     if "ak_patients_code" in msg:
#         raise ValueError("patient_code already exists")
#     raise ValueError("duplicate key / integrity error")


# def _to_read_dict(obj: Patient) -> dict:
#     return PatientRead.model_validate(obj).model_dump()


# def _with_refs(stmt):
#     # โหลด relationship allergies/alerts (ไม่พังแม้ schema ยังไม่ส่ง nested)
#     return stmt.options(
#         selectinload(Patient.allergy),
#         selectinload(Patient.drug_allergy),
#         selectinload(Patient.alert),
#     )



# ==============================
# Sources (core ORM)
# ==============================

async def create_source(db: AsyncSession, data: SourceCreate) -> Source:
    obj = Source(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ✅ replace function เดิม
async def get_all_sources(
    db: AsyncSession,
    q: str = "",
    source_type: str = "",
    is_active: Optional[bool] = None,
) -> List[Source]:
    stmt = select(Source)

    if is_active is not None:
        stmt = stmt.where(Source.is_active == is_active)

    if source_type:
        stmt = stmt.where(Source.source_type == source_type)

    if q:
        stmt = stmt.where(Source.source_name.ilike(f"%{q}%"))

    stmt = stmt.order_by(Source.source_name)
    result = await db.execute(stmt)
    return list(result.scalars().all())



async def get_source_by_id(db: AsyncSession, source_id: UUID) -> Optional[Source]:
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    return result.scalar_one_or_none()


async def update_source_by_id(
    db: AsyncSession,
    source_id: UUID,
    data: SourceUpdate,
) -> Optional[Source]:
    obj = await get_source_by_id(db, source_id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_source_by_id(db: AsyncSession, source_id: UUID) -> bool:
    obj = await get_source_by_id(db, source_id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True


# ==============================
# Sources (router wrappers – ให้ตรงกับ sources.py)
# ==============================

async def post_source_service(
    db: AsyncSession,
    data: SourceCreate,
) -> Source:
    # ใช้ create_source() โดยตรง
    return await create_source(db, data)


# async def get_all_source_service(db: AsyncSession) -> List[Source]:
#     return await get_all_sources(db)
# ✅ ให้ wrapper เรียกอันใหม่
async def get_all_source_service(
    db: AsyncSession,
    q: str = "",
    source_type: str = "",
    is_active: Optional[bool] = None,
) -> List[Source]:
    return await get_all_sources(db, q=q, source_type=source_type, is_active=is_active)


async def get_source_by_id_service(
    db: AsyncSession,
    source_id: UUID,
) -> Optional[Source]:
    return await get_source_by_id(db, source_id)


async def put_source_by_id_service(
    db: AsyncSession,
    source_id: UUID,
    updated: dict,
) -> Optional[Source]:
    """
    updated: dict ที่มาจาก generate_source_update_payload()
    """
    data = SourceUpdate(**updated)
    return await update_source_by_id(db, source_id, data)


async def delete_source_by_id_service(
    db: AsyncSession,
    source_id: UUID,
) -> bool:
    return await delete_source_by_id(db, source_id)


def generate_source_update_payload(sourc: SourceUpdate) -> dict:
    """
    แปลง SourcesUpdateModel → dict (exclude_unset) ให้ router ใช้งานง่าย
    """
    return sourc.model_dump(exclude_unset=True)


def format_source_results(items: List[Source]):
    """
    ตอนนี้ให้ส่ง SQLAlchemy objects กลับไปเลย
    ResponseHandler/jsonable_encoder จะจัดการ serialize ให้
    ถ้าภายหลังอยากใช้ Pydantic สามารถ map เป็น SourceRead ได้
    """
    return items


# ==============================
# Alerts
# ==============================

async def create_alert(db: AsyncSession, data: AlertCreate) -> Alert:
    obj = Alert(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_all_alerts(db: AsyncSession) -> List[Alert]:
    result = await db.execute(
        select(Alert).order_by(Alert.alert_type)
    )
    return list(result.scalars().all())


async def get_alert_by_id(db: AsyncSession, alert_id: UUID) -> Optional[Alert]:
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    return result.scalar_one_or_none()


async def update_alert_by_id(
    db: AsyncSession,
    alert_id: UUID,
    data: AlertUpdate,
) -> Optional[Alert]:
    obj = await get_alert_by_id(db, alert_id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_alert_by_id(db: AsyncSession, alert_id: UUID) -> bool:
    obj = await get_alert_by_id(db, alert_id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True


# ==============================
# Allergies
# ==============================

async def create_allergy(db: AsyncSession, data: AllergyCreate) -> Allergy:
    obj = Allergy(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj



# ต้องมี Allergy ORM model import อยู่แล้วในไฟล์
# from app.db.models import Allergy  (หรือ path ที่คุณใช้จริง)

async def get_all_allergies(
    db: AsyncSession,
    allergy_name: Optional[str] = None,
    allergy_type: Optional[str] = None,
    is_active: bool = True,
) -> List[dict]:
    stmt = select(Allergy).where(Allergy.is_active == is_active)

    if allergy_name:
        stmt = stmt.where(Allergy.allergy_name.ilike(f"%{allergy_name}%"))

    if allergy_type:
        stmt = stmt.where(Allergy.allergy_type == allergy_type)

    stmt = stmt.order_by(Allergy.allergy_name.asc())

    res = await db.execute(stmt)
    rows = res.scalars().all()

    # ✅ serialize แบบตรงไปตรงมา (ไม่ใช้ to_dict)
    return [
        {
            "id": a.id,
            "allergy_name": a.allergy_name,
            "allergy_type": getattr(a, "allergy_type", None),
            "description": getattr(a, "description", None),
            "is_active": getattr(a, "is_active", True),
            "created_at": getattr(a, "created_at", None),
            "updated_at": getattr(a, "updated_at", None),
        }
        for a in rows
    ]



async def get_allergy_by_id(db: AsyncSession, allergy_id: UUID) -> Optional[Allergy]:
    result = await db.execute(
        select(Allergy).where(Allergy.id == allergy_id)
    )
    return result.scalar_one_or_none()


async def update_allergy_by_id(
    db: AsyncSession,
    allergy_id: UUID,
    data: AllergyUpdate,
) -> Optional[Allergy]:
    obj = await get_allergy_by_id(db, allergy_id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_allergy_by_id(db: AsyncSession, allergy_id: UUID) -> bool:
    obj = await get_allergy_by_id(db, allergy_id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True


# ==============================
# Marketing Staff
# ==============================

async def create_marketing_staff(
    db: AsyncSession,
    data: MarketingStaffCreate,
) -> MarketingStaff:
    obj = MarketingStaff(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_all_marketing_staff(db: AsyncSession) -> List[MarketingStaff]:
    result = await db.execute(
        select(MarketingStaff).order_by(MarketingStaff.marketing_name)
    )
    return list(result.scalars().all())


async def get_marketing_staff_by_id(
    db: AsyncSession,
    marketing_staff_id: UUID,
) -> Optional[MarketingStaff]:
    result = await db.execute(
        select(MarketingStaff).where(MarketingStaff.id == marketing_staff_id)
    )
    return result.scalar_one_or_none()


async def update_marketing_staff_by_id(
    db: AsyncSession,
    marketing_staff_id: UUID,
    data: MarketingStaffUpdate,
) -> Optional[MarketingStaff]:
    obj = await get_marketing_staff_by_id(db, marketing_staff_id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_marketing_staff_by_id(
    db: AsyncSession,
    marketing_staff_id: UUID,
) -> bool:
    obj = await get_marketing_staff_by_id(db, marketing_staff_id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True



# ==============================
# Patient Types
# ==============================

async def create_patient_type(
    db: AsyncSession,
    data: PatientTypeCreate,
) -> PatientType:
    obj = PatientType(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_all_patient_types(db: AsyncSession) -> List[PatientType]:
    result = await db.execute(
        select(PatientType).order_by(PatientType.type_name)
    )
    return list(result.scalars().all())


async def get_patient_type_by_id(
    db: AsyncSession,
    patient_type_id: UUID,
) -> Optional[PatientType]:
    result = await db.execute(
        select(PatientType).where(PatientType.id == patient_type_id)
    )
    return result.scalar_one_or_none()


async def update_patient_type_by_id(
    db: AsyncSession,
    patient_type_id: UUID,
    data: PatientTypeUpdate,
) -> Optional[PatientType]:
    obj = await get_patient_type_by_id(db, patient_type_id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_patient_type_by_id(
    db: AsyncSession,
    patient_type_id: UUID,
) -> bool:
    obj = await get_patient_type_by_id(db, patient_type_id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True


# ==============================
# Professions
# ==============================

async def create_profession(
    db: AsyncSession,
    data: ProfessionCreate,
) -> Profession:
    obj = Profession(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_all_professions(db: AsyncSession) -> List[Profession]:
    result = await db.execute(
        select(Profession).order_by(Profession.profession_name)
    )
    return list(result.scalars().all())


async def get_profession_by_id(
    db: AsyncSession,
    profession_id: UUID,
) -> Optional[Profession]:
    result = await db.execute(
        select(Profession).where(Profession.id == profession_id)
    )
    return result.scalar_one_or_none()


async def update_profession_by_id(
    db: AsyncSession,
    profession_id: UUID,
    data: ProfessionUpdate,
) -> Optional[Profession]:
    obj = await get_profession_by_id(db, profession_id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_profession_by_id(
    db: AsyncSession,
    profession_id: UUID,
) -> bool:
    obj = await get_profession_by_id(db, profession_id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True


# ==============================
# Sale Staff
# ==============================

async def create_sale_staff(
    db: AsyncSession,
    data: SaleStaffCreate,
) -> SaleStaff:
    obj = SaleStaff(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_all_sale_staff(db: AsyncSession) -> List[SaleStaff]:
    result = await db.execute(
        select(SaleStaff).order_by(SaleStaff.sale_person_name)
    )
    return list(result.scalars().all())


async def get_sale_staff_by_id(
    db: AsyncSession,
    sale_staff_id: UUID,
) -> Optional[SaleStaff]:
    result = await db.execute(
        select(SaleStaff).where(SaleStaff.id == sale_staff_id)
    )
    return result.scalar_one_or_none()


async def update_sale_staff_by_id(
    db: AsyncSession,
    sale_staff_id: UUID,
    data: SaleStaffUpdate,
) -> Optional[SaleStaff]:
    obj = await get_sale_staff_by_id(db, sale_staff_id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_sale_staff_by_id(
    db: AsyncSession,
    sale_staff_id: UUID,
) -> bool:
    obj = await get_sale_staff_by_id(db, sale_staff_id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True