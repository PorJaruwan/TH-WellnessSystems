# app/api/v1/services/settings_orm_service.py

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Company,
    Location,
    Building,
    Department,
    Room,
    RoomService,
    RoomAvailability,
    Service,
    ServiceType,
)

# --- fields that must be server-managed ---
_AUDIT_FIELDS = {"created_at", "updated_at"}


def _strip_audit_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Prevent client-controlled audit fields from being persisted."""
    return {k: v for k, v in data.items() if k not in _AUDIT_FIELDS}


# ---------- helpers ----------
async def _create(session: AsyncSession, obj):
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def _delete(session: AsyncSession, obj) -> bool:
    await session.delete(obj)
    await session.commit()
    return True


async def _update(session: AsyncSession, obj, data: dict[str, Any]):
    """
    Update model fields safely:
    - strip audit fields
    - let SQLAlchemy model onupdate=func.now() handle updated_at
    """
    data = _strip_audit_fields(data)
    for k, v in data.items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


async def _create_model(session: AsyncSession, model_cls, data: dict[str, Any]):
    """
    DRY helper for create:
    - strip audit fields
    - create model instance
    - commit & refresh
    """
    data = _strip_audit_fields(data)
    obj = model_cls(**data)
    return await _create(session, obj)


# =========================
# Companies
# =========================
async def orm_create_company(session: AsyncSession, data: dict[str, Any]) -> Company:
    return await _create_model(session, Company, data)


async def orm_get_all_companies(session: AsyncSession) -> list[Company]:
    res = await session.execute(select(Company).order_by(Company.company_name.asc()))
    return list(res.scalars().all())


async def orm_get_company_by_code(session: AsyncSession, company_code: str) -> Optional[Company]:
    res = await session.execute(select(Company).where(Company.company_code == company_code))
    return res.scalar_one_or_none()


async def orm_update_company_by_code(
    session: AsyncSession, company_code: str, updated: dict[str, Any]
) -> Optional[Company]:
    obj = await orm_get_company_by_code(session, company_code)
    if not obj:
        return None
    return await _update(session, obj, updated)


async def orm_delete_company_by_code(session: AsyncSession, company_code: str) -> bool:
    obj = await orm_get_company_by_code(session, company_code)
    if not obj:
        return False
    return await _delete(session, obj)


# =========================
# Locations + (extra query) + (active filter)
# =========================
async def orm_create_location(session: AsyncSession, data: dict[str, Any]) -> Location:
    return await _create_model(session, Location, data)


async def orm_get_all_locations(session: AsyncSession) -> list[Location]:
    res = await session.execute(select(Location).order_by(Location.location_name.asc()))
    return list(res.scalars().all())


async def orm_get_location_by_id(session: AsyncSession, location_id: UUID) -> Optional[Location]:
    res = await session.execute(select(Location).where(Location.id == location_id))
    return res.scalar_one_or_none()


async def orm_update_location_by_id(
    session: AsyncSession, location_id: UUID, updated: dict[str, Any]
) -> Optional[Location]:
    obj = await orm_get_location_by_id(session, location_id)
    if not obj:
        return None
    return await _update(session, obj, updated)


async def orm_delete_location_by_id(session: AsyncSession, location_id: UUID) -> bool:
    obj = await orm_get_location_by_id(session, location_id)
    if not obj:
        return False
    return await _delete(session, obj)


async def orm_get_locations_by_company_code(session: AsyncSession, company_code: str) -> list[Location]:
    res = await session.execute(
        select(Location)
        .where(Location.company_code == company_code)
        .order_by(Location.location_name.asc())
    )
    return list(res.scalars().all())


async def orm_get_locations_active(session: AsyncSession, is_active: bool = True) -> list[Location]:
    res = await session.execute(
        select(Location)
        .where(Location.is_active == is_active)
        .order_by(Location.location_name.asc())
    )
    return list(res.scalars().all())


async def orm_get_locations_by_company_code_active(
    session: AsyncSession,
    company_code: str,
    is_active: bool = True,
) -> list[Location]:
    res = await session.execute(
        select(Location)
        .where(Location.company_code == company_code)
        .where(Location.is_active == is_active)
        .order_by(Location.location_name.asc())
    )
    return list(res.scalars().all())


# =========================
# Buildings + (extra query) + (active filter)
# =========================
async def orm_create_building(session: AsyncSession, data: dict[str, Any]) -> Building:
    return await _create_model(session, Building, data)


async def orm_get_all_buildings(session: AsyncSession) -> list[Building]:
    res = await session.execute(select(Building).order_by(Building.building_name.asc()))
    return list(res.scalars().all())


async def orm_get_building_by_id(session: AsyncSession, building_id: UUID) -> Optional[Building]:
    res = await session.execute(select(Building).where(Building.id == building_id))
    return res.scalar_one_or_none()


async def orm_update_building_by_id(
    session: AsyncSession, building_id: UUID, updated: dict[str, Any]
) -> Optional[Building]:
    obj = await orm_get_building_by_id(session, building_id)
    if not obj:
        return None
    return await _update(session, obj, updated)


async def orm_delete_building_by_id(session: AsyncSession, building_id: UUID) -> bool:
    obj = await orm_get_building_by_id(session, building_id)
    if not obj:
        return False
    return await _delete(session, obj)


async def orm_get_buildings_by_location_id(session: AsyncSession, location_id: UUID) -> list[Building]:
    res = await session.execute(
        select(Building)
        .where(Building.location_id == location_id)
        .order_by(Building.building_name.asc())
    )
    return list(res.scalars().all())


async def orm_get_buildings_active(session: AsyncSession, is_active: bool = True) -> list[Building]:
    res = await session.execute(
        select(Building)
        .where(Building.is_active == is_active)
        .order_by(Building.building_name.asc())
    )
    return list(res.scalars().all())


async def orm_get_buildings_by_location_id_active(
    session: AsyncSession,
    location_id: UUID,
    is_active: bool = True,
) -> list[Building]:
    res = await session.execute(
        select(Building)
        .where(Building.location_id == location_id)
        .where(Building.is_active == is_active)
        .order_by(Building.building_name.asc())
    )
    return list(res.scalars().all())


# =========================
# Departments
# =========================
async def orm_create_department(session: AsyncSession, data: dict[str, Any]) -> Department:
    return await _create_model(session, Department, data)


async def orm_get_all_departments(session: AsyncSession) -> list[Department]:
    res = await session.execute(select(Department).order_by(Department.department_name.asc()))
    return list(res.scalars().all())


async def orm_get_department_by_id(session: AsyncSession, department_id: UUID) -> Optional[Department]:
    return await session.get(Department, department_id)


async def orm_update_department_by_id(
    session: AsyncSession, department_id: UUID, data: dict[str, Any]
) -> Optional[Department]:
    obj = await orm_get_department_by_id(session, department_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_department_by_id(session: AsyncSession, department_id: UUID) -> bool:
    obj = await orm_get_department_by_id(session, department_id)
    if not obj:
        return False
    return await _delete(session, obj)


# =========================
# Rooms
# =========================
async def orm_create_room(session: AsyncSession, data: dict[str, Any]) -> Room:
    return await _create_model(session, Room, data)


async def orm_get_all_rooms(session: AsyncSession) -> list[Room]:
    res = await session.execute(select(Room).order_by(Room.room_name.asc()))
    return list(res.scalars().all())


async def orm_get_room_by_id(session: AsyncSession, room_id: UUID) -> Optional[Room]:
    return await session.get(Room, room_id)


async def orm_update_room_by_id(session: AsyncSession, room_id: UUID, data: dict[str, Any]) -> Optional[Room]:
    obj = await orm_get_room_by_id(session, room_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_room_by_id(session: AsyncSession, room_id: UUID) -> bool:
    obj = await orm_get_room_by_id(session, room_id)
    if not obj:
        return False
    return await _delete(session, obj)


# =========================
# Room Services
# =========================
async def orm_create_room_service(session: AsyncSession, data: dict[str, Any]) -> RoomService:
    return await _create_model(session, RoomService, data)


async def orm_get_all_room_services(session: AsyncSession) -> list[RoomService]:
    res = await session.execute(select(RoomService).order_by(RoomService.created_at.desc()))
    return list(res.scalars().all())


async def orm_get_room_service_by_id(session: AsyncSession, room_service_id: UUID) -> Optional[RoomService]:
    return await session.get(RoomService, room_service_id)


async def orm_update_room_service_by_id(
    session: AsyncSession, room_service_id: UUID, data: dict[str, Any]
) -> Optional[RoomService]:
    obj = await orm_get_room_service_by_id(session, room_service_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_room_service_by_id(session: AsyncSession, room_service_id: UUID) -> bool:
    obj = await orm_get_room_service_by_id(session, room_service_id)
    if not obj:
        return False
    return await _delete(session, obj)


# =========================
# Room Availabilities
# =========================
async def orm_create_room_availability(session: AsyncSession, data: dict[str, Any]) -> RoomAvailability:
    return await _create_model(session, RoomAvailability, data)


async def orm_get_all_room_availabilities(session: AsyncSession) -> list[RoomAvailability]:
    res = await session.execute(select(RoomAvailability).order_by(RoomAvailability.available_date.desc()))
    return list(res.scalars().all())


async def orm_get_room_availability_by_id(
    session: AsyncSession, availability_id: UUID
) -> Optional[RoomAvailability]:
    return await session.get(RoomAvailability, availability_id)


async def orm_update_room_availability_by_id(
    session: AsyncSession, availability_id: UUID, data: dict[str, Any]
) -> Optional[RoomAvailability]:
    obj = await orm_get_room_availability_by_id(session, availability_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_room_availability_by_id(session: AsyncSession, availability_id: UUID) -> bool:
    obj = await orm_get_room_availability_by_id(session, availability_id)
    if not obj:
        return False
    return await _delete(session, obj)


# =========================
# Service Types
# =========================
async def orm_create_service_type(session: AsyncSession, data: dict[str, Any]) -> ServiceType:
    return await _create_model(session, ServiceType, data)


async def orm_get_all_service_types(session: AsyncSession) -> list[ServiceType]:
    res = await session.execute(select(ServiceType).order_by(ServiceType.service_type_name.asc()))
    return list(res.scalars().all())


async def orm_get_service_type_by_id(session: AsyncSession, service_type_id: UUID) -> Optional[ServiceType]:
    return await session.get(ServiceType, service_type_id)


async def orm_update_service_type_by_id(
    session: AsyncSession, service_type_id: UUID, data: dict[str, Any]
) -> Optional[ServiceType]:
    obj = await orm_get_service_type_by_id(session, service_type_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_service_type_by_id(session: AsyncSession, service_type_id: UUID) -> bool:
    obj = await orm_get_service_type_by_id(session, service_type_id)
    if not obj:
        return False
    return await _delete(session, obj)


# =========================
# Services
# =========================
async def orm_create_service(session: AsyncSession, data: dict[str, Any]) -> Service:
    return await _create_model(session, Service, data)


async def orm_get_all_services(session: AsyncSession) -> list[Service]:
    res = await session.execute(select(Service).order_by(Service.service_name.asc()))
    return list(res.scalars().all())


async def orm_get_service_by_id(session: AsyncSession, service_id: UUID) -> Optional[Service]:
    return await session.get(Service, service_id)


async def orm_update_service_by_id(session: AsyncSession, service_id: UUID, data: dict[str, Any]) -> Optional[Service]:
    obj = await orm_get_service_by_id(session, service_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_service_by_id(session: AsyncSession, service_id: UUID) -> bool:
    obj = await orm_get_service_by_id(session, service_id)
    if not obj:
        return False
    return await _delete(session, obj)
