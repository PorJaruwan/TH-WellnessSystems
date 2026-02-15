# app/db/models/booking_settings.py

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Core
    from app.db.models.core_settings import Company, Location, Building, Room, Service
    # Patient/Staff
    from app.db.models.patient_settings import Patient
    from app.db.models.staff_settings import Staff


# ==========================================================
# BOOKINGS
# ==========================================================
class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        # ---- Checks (ตาม schema) ----
        CheckConstraint(
            "(status)::text = any (array['available','draft','booked','confirmed','checked_in','in_service','completed','cancelled','no_show','rescheduled']::text[])",
            name="ckc_status_bookings",
        ),
        CheckConstraint(
            "(source_of_ad is null) OR ((source_of_ad)::text = any (array['online','walk_in','call_center','line']::text[]))",
            name="ckc_source_of_ad_bookings",
        ),
        # ---- Indexes (ตาม schema) ----
        Index("idx_bookings_building_room_date", "building_id", "room_id", "booking_date"),
        Index("idx_bookings_company_loc_date", "company_code", "location_id", "booking_date"),
        Index("idx_bookings_booking_date", "booking_date"),
    )

    # ---- PK ----
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ---- Required FKs ----
    resource_track_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    company_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("companies.company_code"),
        nullable=False,
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("locations.id"),
        nullable=False,
    )
    building_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("buildings.id"),
        nullable=False,
    )
    room_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("rooms.id"),
        nullable=False,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.id"),
        nullable=False,
    )
    primary_person_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id"),
        nullable=False,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("services.id"),
        nullable=False,
    )

    # ---- Booking info ----
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("CURRENT_DATE"))

    # ✅ Standard/clarity: explicit Time type (time without time zone)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    status: Mapped[str] = mapped_column(String(25), nullable=False)

    source_of_ad: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancel_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ---- Audit ----
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ==========================================================
    # Relationships (back_populates ready; string-based to avoid circular import)
    # ==========================================================
    company: Mapped["Company"] = relationship("Company", lazy="selectin", back_populates="bookings")
    location: Mapped["Location"] = relationship("Location", lazy="selectin", back_populates="bookings")
    building: Mapped["Building"] = relationship("Building", lazy="selectin", back_populates="bookings")
    room: Mapped["Room"] = relationship("Room", lazy="selectin", back_populates="bookings")

    patient: Mapped["Patient"] = relationship("Patient", lazy="selectin", back_populates="bookings")

    primary_person: Mapped["Staff"] = relationship(
        "Staff",
        lazy="selectin",
        foreign_keys="Booking.primary_person_id",
        back_populates="primary_bookings",
    )

    service: Mapped["Service"] = relationship("Service", lazy="selectin", back_populates="bookings")

    status_histories: Mapped[List["BookingStatusHistory"]] = relationship(
        "BookingStatusHistory",
        lazy="selectin",
        cascade="all, delete-orphan",
        back_populates="booking",
    )

    booking_staffs: Mapped[List["BookingStaff"]] = relationship(
        "BookingStaff",
        lazy="selectin",
        cascade="all, delete-orphan",
        back_populates="booking",
    )


# ==========================================================
# BOOKING VIEW CONFIG
# ==========================================================
class BookingViewConfig(Base):
    __tablename__ = "booking_view_config"
    __table_args__ = (
        CheckConstraint(
            "(group_by is null) OR ((group_by)::text = any (array['building','room_type','track_type']::text[]))",
            name="ckc_group_by_booking",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    company_code: Mapped[str] = mapped_column(String(50), ForeignKey("companies.company_code"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("buildings.id"), nullable=False)

    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    max_columns: Mapped[int] = mapped_column(Integer, nullable=False)

    group_by: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ---- Relationships ----
    company: Mapped["Company"] = relationship("Company", lazy="selectin")
    location: Mapped["Location"] = relationship("Location", lazy="selectin")
    building: Mapped["Building"] = relationship("Building", lazy="selectin")


# ==========================================================
# BOOKING STATUS HISTORY
# ==========================================================
class BookingStatusHistory(Base):
    __tablename__ = "booking_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    old_status: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)

    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    booking_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("bookings.id"),
        nullable=False,
    )

    # ---- Relationships ----
    booking: Mapped["Booking"] = relationship(
        "Booking",
        lazy="selectin",
        back_populates="status_histories",
    )


# ==========================================================
# BOOKING STAFF
# ==========================================================
class BookingStaff(Base):
    __tablename__ = "booking_staff"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    booking_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("bookings.id"),
        nullable=False,
    )
    staff_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(String(25), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # relationships
    booking: Mapped["Booking"] = relationship(
        "Booking",
        lazy="selectin",
        back_populates="booking_staffs",
    )
    staff: Mapped["Staff"] = relationship(
        "Staff",
        lazy="selectin",
        foreign_keys="BookingStaff.staff_id",
        back_populates="booking_staffs",
    )
