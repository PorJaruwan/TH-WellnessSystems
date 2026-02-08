# app/api/v1/services/settings_orm_service.py

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
    Country,
    Province,
    City,
    District,
    Currency,
    Language,
    Geography,
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
    res = await session.execute(
        select(Building)
        .options(
            selectinload(Building.location)  # ✅ IMPORTANT
        )
        .order_by(Building.building_name.asc())
    )
    return list(res.scalars().all())

async def orm_get_buildings_by_location_id(session: AsyncSession, location_id: UUID) -> list[Building]:
    res = await session.execute(
        select(Building)
        .options(selectinload(Building.location))  #Add
        .where(Building.location_id == location_id)
        .order_by(Building.building_name.asc())
    )
    return list(res.scalars().all())

async def orm_get_buildings_active(
    session: AsyncSession,
    is_active: bool = True,
) -> list[Building]:
    res = await session.execute(
        select(Building)
        .options(selectinload(Building.location))  #Add
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
        .options(selectinload(Building.location))   ##Add
        .where(Building.location_id == location_id)
        .where(Building.is_active == is_active)
        .order_by(Building.building_name.asc())
    )
    return list(res.scalars().all())

async def orm_get_building_by_id(session: AsyncSession, building_id: UUID) -> Optional[Building]:
    res = await session.execute(
        select(Building)
        .options(selectinload(Building.location))  #Add
        .where(Building.id == building_id)
        )
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


async def orm_get_room_by_id_with_names(session: AsyncSession, room_id: UUID) -> Optional[Room]:
    res = await session.execute(
        select(Room)
        .options(
            selectinload(Room.location),
            selectinload(Room.building),
            selectinload(Room.room_type),
        )
        .where(Room.id == room_id)
    )
    return res.scalar_one_or_none()


# =========================
# Room Services
# =========================
async def orm_create_room_service(session: AsyncSession, data: dict[str, Any]) -> RoomService:
    return await _create_model(session, RoomService, data)


async def orm_get_all_room_services(session: AsyncSession) -> list[RoomService]:
    res = await session.execute(
        select(RoomService)
        .options(
            selectinload(RoomService.room),
            selectinload(RoomService.service),
        )
        .order_by(RoomService.created_at.desc()))
    return list(res.scalars().all())


async def orm_get_room_service_by_id(session: AsyncSession, room_service_id: UUID) -> Optional[RoomService]:
    stmt = (
        select(RoomService)
        .options(
            selectinload(RoomService.room),
            selectinload(RoomService.service),
        )
        .where(RoomService.id == room_service_id)
    )
    return (await session.execute(stmt)).scalars().first()


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
    stmt = (
        select(Service)
        .options(selectinload(Service.service_type))  # ✅ CHANGED
        .where(Service.id == service_id)
    )
    return (await session.execute(stmt)).scalars().first()

# async def orm_get_service_by_id(session: AsyncSession, service_id: UUID) -> Optional[Service]:
#     return await session.get(Service, service_id)


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



# =========================
# Countries (Address Settings)
# =========================
async def orm_create_country(session: AsyncSession, data: dict[str, Any]) -> Country:
    return await _create_model(session, Country, data)


async def orm_get_all_countries(session: AsyncSession) -> list[Country]:
    res = await session.execute(select(Country).order_by(Country.name_lo.asc()))
    return list(res.scalars().all())


async def orm_get_country_by_code(session: AsyncSession, country_code: str) -> Optional[Country]:
    res = await session.execute(select(Country).where(Country.country_code == country_code))
    return res.scalar_one_or_none()


async def orm_update_country_by_code(
    session: AsyncSession, country_code: str, data: dict[str, Any]
) -> Optional[Country]:
    obj = await orm_get_country_by_code(session, country_code)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_country_by_code(session: AsyncSession, country_code: str) -> bool:
    obj = await orm_get_country_by_code(session, country_code)
    if not obj:
        return False
    return await _delete(session, obj)


async def orm_get_countries_active(session: AsyncSession, is_active: bool = True) -> list[Country]:
    res = await session.execute(
        select(Country)
        .where(Country.is_active == is_active)
        .order_by(Country.name_lo.asc())
    )
    return list(res.scalars().all())


# =========================
# Provinces (Address Settings)
# =========================
async def orm_create_province(session: AsyncSession, data: dict[str, Any]) -> Province:
    return await _create_model(session, Province, data)


async def orm_get_all_provinces(session: AsyncSession) -> list[Province]:
    res = await session.execute(select(Province).order_by(Province.name_lo.asc()))
    return list(res.scalars().all())


async def orm_get_province_by_id(session: AsyncSession, province_id: int) -> Optional[Province]:
    return await session.get(Province, province_id)


async def orm_update_province_by_id(
    session: AsyncSession, province_id: int, data: dict[str, Any]
) -> Optional[Province]:
    obj = await orm_get_province_by_id(session, province_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_province_by_id(session: AsyncSession, province_id: int) -> bool:
    obj = await orm_get_province_by_id(session, province_id)
    if not obj:
        return False
    return await _delete(session, obj)


async def orm_get_provinces_by_country_code(
    session: AsyncSession, country_code: str
) -> list[Province]:
    res = await session.execute(
        select(Province)
        .where(Province.country_code == country_code)
        .order_by(Province.name_lo.asc())
    )
    return list(res.scalars().all())


async def orm_get_provinces_by_country_code_active(
    session: AsyncSession,
    country_code: str,
    is_active: bool = True,
) -> list[Province]:
    res = await session.execute(
        select(Province)
        .where(Province.country_code == country_code)
        .where(Province.is_active == is_active)
        .order_by(Province.name_lo.asc())
    )
    return list(res.scalars().all())


# =========================
# Cities (Address Settings)
# =========================
async def orm_create_city(session: AsyncSession, data: dict[str, Any]) -> City:
    return await _create_model(session, City, data)


async def orm_get_all_cities(session: AsyncSession) -> list[City]:
    # ตามมาตรฐาน router เมือง: order by id
    res = await session.execute(select(City).order_by(City.id.asc()))
    return list(res.scalars().all())


async def orm_get_city_by_id(session: AsyncSession, city_id: int) -> Optional[City]:
    return await session.get(City, city_id)


async def orm_update_city_by_id(session: AsyncSession, city_id: int, data: dict[str, Any]) -> Optional[City]:
    obj = await orm_get_city_by_id(session, city_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_city_by_id(session: AsyncSession, city_id: int) -> bool:
    obj = await orm_get_city_by_id(session, city_id)
    if not obj:
        return False
    return await _delete(session, obj)


async def orm_get_cities_by_province_id(session: AsyncSession, province_id: int) -> list[City]:
    res = await session.execute(
        select(City)
        .where(City.province_id == province_id)
        .order_by(City.id.asc())
    )
    return list(res.scalars().all())


async def orm_get_cities_by_province_id_active(
    session: AsyncSession,
    province_id: int,
    is_active: bool = True,
) -> list[City]:
    res = await session.execute(
        select(City)
        .where(City.province_id == province_id)
        .where(City.is_active == is_active)
        .order_by(City.id.asc())
    )
    return list(res.scalars().all())


# =========================
# Districts (Address Settings)
# =========================
async def orm_create_district(session: AsyncSession, data: dict[str, Any]) -> District:
    return await _create_model(session, District, data)


async def orm_get_all_districts(session: AsyncSession) -> list[District]:
    res = await session.execute(select(District).order_by(District.name_lo.asc()))
    return list(res.scalars().all())


async def orm_get_district_by_id(session: AsyncSession, district_id: int) -> Optional[District]:
    return await session.get(District, district_id)


async def orm_update_district_by_id(
    session: AsyncSession, district_id: int, data: dict[str, Any]
) -> Optional[District]:
    obj = await orm_get_district_by_id(session, district_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_district_by_id(session: AsyncSession, district_id: int) -> bool:
    obj = await orm_get_district_by_id(session, district_id)
    if not obj:
        return False
    return await _delete(session, obj)


async def orm_get_districts_by_city_id(session: AsyncSession, city_id: int) -> list[District]:
    res = await session.execute(
        select(District)
        .where(District.city_id == city_id)
        .order_by(District.name_lo.asc())
    )
    return list(res.scalars().all())


async def orm_get_districts_by_city_id_active(
    session: AsyncSession,
    city_id: int,
    is_active: bool = True,
) -> list[District]:
    res = await session.execute(
        select(District)
        .where(District.city_id == city_id)
        .where(District.is_active == is_active)
        .order_by(District.name_lo.asc())
    )
    return list(res.scalars().all())


# =========================
# Currencies
# =========================
async def orm_create_currency(session: AsyncSession, data: dict[str, Any]) -> Currency:
    return await _create_model(session, Currency, data)


async def orm_get_all_currencies(session: AsyncSession) -> list[Currency]:
    res = await session.execute(select(Currency).order_by(Currency.currency_code.asc()))
    return list(res.scalars().all())


async def orm_get_currency_by_code(session: AsyncSession, currency_code: str) -> Optional[Currency]:
    return await session.get(Currency, currency_code)


async def orm_update_currency_by_code(
    session: AsyncSession, currency_code: str, data: dict[str, Any]
) -> Optional[Currency]:
    obj = await orm_get_currency_by_code(session, currency_code)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_currency_by_code(session: AsyncSession, currency_code: str) -> bool:
    obj = await orm_get_currency_by_code(session, currency_code)
    if not obj:
        return False
    return await _delete(session, obj)


# =========================
# Languages
# =========================
async def orm_create_language(session: AsyncSession, data: dict[str, Any]) -> Language:
    return await _create_model(session, Language, data)


async def orm_get_all_languages(session: AsyncSession) -> list[Language]:
    res = await session.execute(select(Language).order_by(Language.language_code.asc()))
    return list(res.scalars().all())


async def orm_get_language_by_code(session: AsyncSession, language_code: str) -> Optional[Language]:
    return await session.get(Language, language_code)


async def orm_update_language_by_code(
    session: AsyncSession, language_code: str, data: dict[str, Any]
) -> Optional[Language]:
    obj = await orm_get_language_by_code(session, language_code)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_language_by_code(session: AsyncSession, language_code: str) -> bool:
    obj = await orm_get_language_by_code(session, language_code)
    if not obj:
        return False
    return await _delete(session, obj)


# =========================
# Geographies
# =========================
async def orm_create_geography(session: AsyncSession, data: dict[str, Any]) -> Geography:
    return await _create_model(session, Geography, data)


async def orm_get_all_geographies(session: AsyncSession) -> list[Geography]:
    res = await session.execute(select(Geography).order_by(Geography.id.asc()))
    return list(res.scalars().all())


async def orm_get_geography_by_id(session: AsyncSession, geography_id: int) -> Optional[Geography]:
    return await session.get(Geography, geography_id)


async def orm_update_geography_by_id(
    session: AsyncSession, geography_id: int, data: dict[str, Any]
) -> Optional[Geography]:
    obj = await orm_get_geography_by_id(session, geography_id)
    if not obj:
        return None
    return await _update(session, obj, data)


async def orm_delete_geography_by_id(session: AsyncSession, geography_id: int) -> bool:
    obj = await orm_get_geography_by_id(session, geography_id)
    if not obj:
        return False
    return await _delete(session, obj)
