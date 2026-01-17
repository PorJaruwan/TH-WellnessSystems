# app/db/models/patient.py
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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
    payment_status: Mapped[str] = mapped_column(String(25), nullable=False)
    contact_phone1: Mapped[str] = mapped_column(String(25), nullable=False)
    full_name_lo: Mapped[str] = mapped_column(String(255), nullable=False)

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
