# app/db/models/patient_settings.py
from __future__ import annotations

from uuid import UUID
import uuid

from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import (Boolean, CheckConstraint, Date, DateTime, 
    ForeignKey, String, Text, text, UniqueConstraint,func,
    )
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.db.models.patient_settings import Alert, Allergy
    from app.db.models.booking_settings import Booking


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (
        UniqueConstraint("email", name="ak_patients_email"),
        UniqueConstraint("id_card_no", name="ak_patients_id_card_no"),
        UniqueConstraint("patient_code", name="ak_patients_code"),
        CheckConstraint(
            "(sex is null) OR (sex in ('male','female','lgbtq'))",
            name="patients_sex_check",
        ),
        CheckConstraint(
            "(main_contact_method is null) OR (main_contact_method in ('phone','email','text'))",
            name="main_contact_method_check",
        ),
    )

    # ==========================================================
    # Primary key
    # ==========================================================
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ==========================================================
    # Required fields (NOT NULL in DB)
    # ==========================================================
    patient_code: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name_lo: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name_lo: Mapped[str] = mapped_column(String(100), nullable=False)
    id_card_no: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name_lo: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(25), nullable=False)
    payment_status: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    contact_phone1: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    

    # ==========================================================
    # Optional fields
    # ==========================================================
    title_en: Mapped[Optional[str]] = mapped_column(String(25))
    first_name_en: Mapped[Optional[str]] = mapped_column(String(100))
    last_name_en: Mapped[Optional[str]] = mapped_column(String(100))

    title_lo: Mapped[Optional[str]] = mapped_column(String(25))
    title_cc: Mapped[Optional[str]] = mapped_column(String(25))

    social_security_id: Mapped[Optional[str]] = mapped_column(String(25))

    sex: Mapped[Optional[str]] = mapped_column(String(20))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    religion: Mapped[Optional[str]] = mapped_column(String(255))

    telephone: Mapped[Optional[str]] = mapped_column(String(25))
    work_phone: Mapped[Optional[str]] = mapped_column(String(25))

    line_id: Mapped[Optional[str]] = mapped_column(String(100))
    facebook: Mapped[Optional[str]] = mapped_column(String(100))
    whatsapp: Mapped[Optional[str]] = mapped_column(String(100))

    # ==========================================================
    # Foreign keys (UUID plain – ยังไม่ bind ORM ของ table ปลายทาง)
    # ==========================================================
    profession_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))
    patient_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))
    customer_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))
    salesperson_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))
    marketing_person_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))
    locations_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))

    # ==========================================================
    # Notes / contacts
    # ==========================================================
    allergy_note: Mapped[Optional[str]] = mapped_column(Text)

    contact_first_name: Mapped[Optional[str]] = mapped_column(String(100))
    contact_last_name: Mapped[Optional[str]] = mapped_column(String(100))
    contact_phone2: Mapped[Optional[str]] = mapped_column(String(25))

    # ⚠️ เปลี่ยนชื่อ field เพื่อไม่ชน sqlalchemy.orm.relationship
    # DB column ยังชื่อ "relationship"
    contact_relationship: Mapped[Optional[str]] = mapped_column(
        "relationship",
        String(255),
    )

    alert_note: Mapped[Optional[str]] = mapped_column(Text)

    patient_note: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(25))

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    full_name_en: Mapped[Optional[str]] = mapped_column(String(255))
    main_contact_method: Mapped[Optional[str]] = mapped_column(String(25))

    alert_level: Mapped[Optional[str]] = mapped_column(String(25))
    critical_medical_note: Mapped[Optional[str]] = mapped_column(Text)

    # ==========================================================
    # Timestamps (from DB)
    # ==========================================================
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ==========================================================
    # Relationships (เริ่มจาก allergies / alerts)
    # ==========================================================
    allergy_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("allergies.id", ondelete="SET NULL"),
    )
    drug_allergy_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("allergies.id", ondelete="SET NULL"),
    )
    alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("alerts.id", ondelete="SET NULL"),
    )

    allergy: Mapped[Optional["Allergy"]] = relationship(
        "Allergy",
        foreign_keys=[allergy_id],
        lazy="selectin",
    )
    drug_allergy: Mapped[Optional["Allergy"]] = relationship(
        "Allergy",
        foreign_keys=[drug_allergy_id],
        lazy="selectin",
    )
    alert: Mapped[Optional["Alert"]] = relationship(
        "Alert",
        foreign_keys=[alert_id],
        lazy="selectin",
    )
    market_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))  # ✅ NEW
    referral_source_note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # ✅ NEW
    market_source_note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)    # ✅ NEW
    
    # ==========================================================
    # Bookings
    # ==========================================================
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="patient",
        lazy="selectin",
    )



########################
# from sqlalchemy import Index
# __table_args__ = (
#   ... เดิม ...,
#   Index("idx_patients_patient_code", "patient_code"),
#   Index("idx_patients_id_card_no", "id_card_no"),
#   Index("idx_patients_telephone", "telephone"),
#   Index("idx_patients_created_at", "created_at"),
# )
# ถ้ามี Patient ORM ภายหลัง ค่อยมาเพิ่ม relationship + TYPE_CHECKING ทีหลังได้

###===== Patient-child and related=====###
class PatientAddress(Base):
    __tablename__ = "patient_addresses"

    patient_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id"),
        primary_key=True,
    )
    address_type: Mapped[str] = mapped_column(String(25), primary_key=True)

    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sub_district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state_province: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    full_address_lo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    full_address_en: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class PatientImage(Base):
    __tablename__ = "patient_images"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    patient_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    image_type: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class PatientPhoto(Base):
    __tablename__ = "patient_photos"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    patient_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id"),
        nullable=False,
        unique=True,
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )



class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    alert_type: Mapped[str] = mapped_column(String(25), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Allergy(Base):
    __tablename__ = "allergies"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    allergy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    allergy_type: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)


class MarketingStaff(Base):
    __tablename__ = "marketing_staff"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    marketing_name: Mapped[str] = mapped_column(String(255), nullable=False)
    campaign: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class PatientType(Base):
    __tablename__ = "patient_types"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    type_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Profession(Base):
    __tablename__ = "professions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    profession_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class SaleStaff(Base):
    __tablename__ = "sale_staff"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    sale_person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )



class Source(Base):
    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # ✅ NEW

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    
