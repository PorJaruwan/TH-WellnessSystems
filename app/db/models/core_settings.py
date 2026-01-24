from __future__ import annotations

from datetime import datetime, date, time
from typing import Optional, List
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Date ,Time, Float, String, text, Text, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.db.models.core_settings import Company
    from app.db.models.core_settings import Location
    from app.db.models.core_settings import Building
    from app.db.models.core_settings import RoomService
    from app.db.models.core_settings import RoomAvailability
    from app.db.models.core_settings import Room
    from app.db.models.core_settings import Service
###=======



###=====companies=====###
class Company(Base):
    __tablename__ = "companies"

    company_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name_en: Mapped[str] = mapped_column(String(255), nullable=False)

    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    address_line3: Mapped[Optional[str]] = mapped_column(String(255))
    address_line1_en: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2_en: Mapped[Optional[str]] = mapped_column(String(255))
    address_line3_en: Mapped[Optional[str]] = mapped_column(String(255))

    post_code: Mapped[Optional[str]] = mapped_column(String(25))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    telephone: Mapped[Optional[str]] = mapped_column(String(25))
    fax: Mapped[Optional[str]] = mapped_column(String(25))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    domain_name: Mapped[Optional[str]] = mapped_column(String(255))
    tax_id: Mapped[Optional[str]] = mapped_column(String(25))
    vat_rate: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("0"))

    branch_id: Mapped[Optional[str]] = mapped_column(String(25))
    branch_name: Mapped[Optional[str]] = mapped_column(String(255))
    head_office: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text("false"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    company_type: Mapped[Optional[str]] = mapped_column(String(50))

    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    locations: Mapped[List["Location"]] = relationship(
        "Location",
        back_populates="company",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


###=====departments=====###
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    company_code: Mapped[str] = mapped_column(String, nullable=False)

    department_name: Mapped[str] = mapped_column(String, nullable=False)
    department_code: Mapped[Optional[str]] = mapped_column(String)
    department_type_id: Mapped[Optional[str]] = mapped_column(String)
    head_id: Mapped[Optional[str]] = mapped_column(String)

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())



###=====locations=====###
class Location(Base):
    __tablename__ = "locations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

    company_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("companies.company_code", ondelete="RESTRICT"),
        nullable=False,
    )

    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_type: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(String(500))
    phone: Mapped[Optional[str]] = mapped_column(String(25))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    location_code: Mapped[Optional[str]] = mapped_column(String(50))
    manager_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="locations")
    buildings: Mapped[List["Building"]] = relationship(
        "Building",
        back_populates="location",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )



###=====buildings=====###

class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

    company_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("companies.company_code", ondelete="RESTRICT"),
        nullable=False,
    )

    location_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    building_code: Mapped[str] = mapped_column(String(50), nullable=False)
    building_name: Mapped[str] = mapped_column(String(255), nullable=False)
    floors: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    building_type: Mapped[Optional[str]] = mapped_column(String(50))
    reason: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    location: Mapped["Location"] = relationship("Location", back_populates="buildings")



###=====rooms=====###

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    location_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    building_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("buildings.id"), nullable=False)

    room_code: Mapped[str] = mapped_column(String, nullable=False)
    room_name: Mapped[str] = mapped_column(String, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, server_default=text("1"))

    is_available: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))

    room_type_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    floor_number: Mapped[Optional[int]] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    room_services: Mapped[list["RoomService"]] = relationship(
        "RoomService",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    availabilities: Mapped[list["RoomAvailability"]] = relationship(
        "RoomAvailability",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    location: Mapped["Location"] = relationship(
        "Location",
        foreign_keys=[location_id],
    )

    building: Mapped["Building"] = relationship(
        "Building",
        foreign_keys=[building_id],
    )


###=====room_availabilities=====###

class RoomAvailability(Base):
    __tablename__ = "room_availabilities"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    room_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)

    available_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    room: Mapped["Room"] = relationship("Room", back_populates="availabilities")


###=====room_services=====###

class RoomService(Base):
    __tablename__ = "room_services"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    room_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    service_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)

    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="room_services")
    service: Mapped["Service"] = relationship("Service", back_populates="room_services")


###=====service_types=====###
class ServiceType(Base):
    __tablename__ = "service_types"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    service_type_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    services: Mapped[list["Service"]] = relationship("Service", back_populates="service_type")


###=====services=====###

class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        Index("idx_services_service_type_id", "service_type_id"),
        Index("idx_services_is_active", "is_active"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    service_name: Mapped[str] = mapped_column(String, nullable=False)
    service_type_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("service_types.id"), nullable=False)

    service_price: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # minutes
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    service_type: Mapped["ServiceType"] = relationship("ServiceType", back_populates="services")
    room_services: Mapped[list["RoomService"]] = relationship("RoomService", back_populates="service")
