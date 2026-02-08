# app/db/models/staff_settings.py

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    Index,
    text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.core_settings import Company, Department, Location, Building, Room, Service
    from app.db.models.booking_settings import Booking, BookingStaff


# =========================================================
# Staff
# =========================================================
class Staff(Base):
    __tablename__ = "staff"
    __table_args__ = (
        UniqueConstraint("email", name="ak_staff_email"),
        UniqueConstraint("phone", name="ak_staff_phone"),
        CheckConstraint(
            "(role in ('doctor','therapist','nurse','staff'))",
            name="person_role_check",
        ),
        Index("idx_staff_name", "staff_name"),
        # partial index idx_staff_active_doctor อยู่ใน DB แล้ว; ถ้าจะประกาศใน ORM ต้องใช้ postgresql_where
        # แต่ไม่จำเป็นสำหรับ runtime ORM
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    staff_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)

    license_number: Mapped[Optional[str]] = mapped_column(String(25))
    specialty: Mapped[Optional[str]] = mapped_column(String(255))

    phone: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    gender: Mapped[Optional[str]] = mapped_column(String(20))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    main_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="SET NULL"),
    )
    main_building_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("buildings.id", ondelete="SET NULL"),
    )
    main_room_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="SET NULL"),
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

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

    # Relationships (optional, ช่วย join/serialize)
    main_location: Mapped[Optional["Location"]] = relationship("Location", foreign_keys=[main_location_id], lazy="selectin")
    main_building: Mapped[Optional["Building"]] = relationship("Building", foreign_keys=[main_building_id], lazy="selectin")
    main_room: Mapped[Optional["Room"]] = relationship("Room", foreign_keys=[main_room_id], lazy="selectin")

    departments: Mapped[List["StaffDepartment"]] = relationship(
        "StaffDepartment", back_populates="staff", cascade="all, delete-orphan", lazy="selectin"
    )
    locations: Mapped[List["StaffLocation"]] = relationship(
        "StaffLocation", back_populates="staff", cascade="all, delete-orphan", lazy="selectin"
    )
    services: Mapped[List["StaffService"]] = relationship(
        "StaffService", back_populates="staff", cascade="all, delete-orphan", lazy="selectin"
    )
    
    
    # ==========================================================
    # Bookings (doctor / primary person)
    # ==========================================================
    primary_bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="primary_person",          # ✅ ต้องตรงกับ Booking.primary_person
        foreign_keys="Booking.primary_person_id",
        lazy="selectin",
    )

    # ==========================================================
    # Booking staffs (many-to-many via booking_staff)
    # ==========================================================
    booking_staffs: Mapped[List["BookingStaff"]] = relationship(
        "BookingStaff",
        back_populates="staff",                   # ✅ ต้องตรงกับ BookingStaff.staff
        lazy="selectin",
    )







# =========================================================
# Staff Departments
# =========================================================
class StaffDepartment(Base):
    __tablename__ = "staff_departments"
    __table_args__ = (
        UniqueConstraint("staff_id", "department_id", name="ak_staff_departments"),
        Index("idx_staff_departments_staff", "staff_id"),
        Index("idx_staff_departments_department", "department_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
    )

    role_in_dept: Mapped[Optional[str]] = mapped_column(String(100))
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    staff: Mapped["Staff"] = relationship("Staff", back_populates="departments", lazy="selectin")
    department: Mapped["Department"] = relationship("Department", lazy="selectin")


# =========================================================
# Staff Locations
# =========================================================
class StaffLocation(Base):
    __tablename__ = "staff_locations"
    __table_args__ = (
        UniqueConstraint("staff_id", "location_id", name="ak_staff_locations"),
        Index("idx_staff_locations_staff", "staff_id"),
        Index("idx_staff_locations_location", "location_id"),
        # idx_staff_locations_loc_active เป็น partial index ใน DB
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
    )

    work_days: Mapped[Optional[str]] = mapped_column(String(50))
    work_time_from: Mapped[Optional[time]] = mapped_column(Time)
    work_time_to: Mapped[Optional[time]] = mapped_column(Time)

    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    staff: Mapped["Staff"] = relationship("Staff", back_populates="locations", lazy="selectin")
    location: Mapped["Location"] = relationship("Location", lazy="selectin")


# =========================================================
# Staff Services
# =========================================================
class StaffService(Base):
    __tablename__ = "staff_services"
    __table_args__ = (
        UniqueConstraint("staff_id", "service_id", name="ak_staff_services"),
        # idx_staff_services_staff_active_service เป็น partial index ใน DB
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
    )

    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("30"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    staff: Mapped["Staff"] = relationship("Staff", back_populates="services", lazy="selectin")
    service: Mapped["Service"] = relationship("Service", lazy="selectin")


# =========================================================
# Staff Template
# =========================================================
class StaffTemplate(Base):
    __tablename__ = "staff_template"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    shift_code: Mapped[str] = mapped_column(String(10), nullable=False)
    shift_name: Mapped[Optional[str]] = mapped_column(String(255))

    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_overnight: Mapped[bool] = mapped_column(Boolean, nullable=False)

    description: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


# =========================================================
# Staff Work Pattern
# =========================================================
class StaffWorkPattern(Base):
    __tablename__ = "staff_work_pattern"
    __table_args__ = (
        CheckConstraint("(weekday = any (array[0,1,2,3,4,5,6]))", name="ckc_weekday_staff_wo"),
        # idx_work_pattern_staff_loc_weekday_active เป็น partial index ใน DB
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)

    shift_template_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("staff_template.id", ondelete="CASCADE"), nullable=False)

    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    staff: Mapped["Staff"] = relationship("Staff", lazy="selectin")
    location: Mapped["Location"] = relationship("Location", lazy="selectin")
    department: Mapped["Department"] = relationship("Department", lazy="selectin")
    shift_template: Mapped["StaffTemplate"] = relationship("StaffTemplate", lazy="selectin")


# =========================================================
# Staff Leave
# =========================================================
class StaffLeave(Base):
    __tablename__ = "staff_leave"
    __table_args__ = (
        CheckConstraint(
            "(part_of_day is null) OR (part_of_day in ('full','morning','afternoon'))",
            name="ckc_part_of_day_staff_le",
        ),
        CheckConstraint(
            "(status in ('draft','pending','approved','rejected'))",
            name="order_transactions_status_check",
        ),
        CheckConstraint(
            "(leave_type in ('sick','vacation','personal','other'))",
            name="ckc_leave_type_staff_le",
        ),
        # idx_staff_leave_staff_loc_approved_active เป็น partial index ใน DB
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    company_code: Mapped[str] = mapped_column(String(50), ForeignKey("companies.company_code", ondelete="CASCADE"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    staff_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)

    leave_type: Mapped[str] = mapped_column(String(25), nullable=False)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)

    part_of_day: Mapped[Optional[str]] = mapped_column(String(25))
    status: Mapped[str] = mapped_column(String(25), nullable=False)

    reason: Mapped[Optional[str]] = mapped_column(String(500))

    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True))

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    company: Mapped[Optional["Company"]] = relationship("Company", lazy="selectin")
    location: Mapped[Optional["Location"]] = relationship("Location", lazy="selectin")
    staff: Mapped[Optional["Staff"]] = relationship("Staff", lazy="selectin")



# -------------------------------------------------------------------
# Backward-compatible aliases (fix ImportError from app.db.models.__init__)
# -------------------------------------------------------------------
# Some old modules import these names. Map them to current models.
StaffAvailabilities = StaffWorkPattern
StaffUnavailabilities = StaffLeave


