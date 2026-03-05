from __future__ import annotations

from fastapi import APIRouter

# import routers (from files) ✅ avoid circular import
from .companies_search_router import router as companies_search_router
from .companies_grid_router import router as companies_grid_router
from .companies_read_router import router as companies_read_router
from .companies_router import router as companies_router

from .countries_search_router import router as countries_search_router
from .countries_grid_router import router as countries_grid_router
from .countries_read_router import router as countries_read_router
from .countries_router import router as countries_router

from .currencies_search_router import router as currencies_search_router
from .currencies_grid_router import router as currencies_grid_router

from .geographies_search_router import router as geographies_search_router
from .geographies_grid_router import router as geographies_grid_router
from .languages_search_router import router as languages_search_router
from .languages_grid_router import router as languages_grid_router

from .provinces_search_router import router as provinces_search_router
from .provinces_grid_router import router as provinces_grid_router
from .provinces_read_router import router as provinces_read_router
from .provinces_router import router as provinces_router

from .cities_search_router import router as cities_search_router
from .cities_grid_router import router as cities_grid_router
from .cities_read_router import router as cities_read_router
from .cities_router import router as cities_router

from .districts_search_router import router as districts_search_router
from .districts_grid_router import router as districts_grid_router
from .districts_read_router import router as districts_read_router
from .districts_router import router as districts_router

from .departments_search_router import router as departments_search_router
from .departments_grid_router import router as departments_grid_router
from .departments_read_router import router as departments_read_router
from .departments_router import router as departments_router

from .locations_search_router import router as locations_search_router
from .locations_grid_router import router as locations_grid_router
from .locations_read_router import router as locations_read_router
from .locations_router import router as locations_router

from .buildings_search_router import router as buildings_search_router
from .buildings_grid_router import router as buildings_grid_router
from .buildings_read_router import router as buildings_read_router
from .buildings_router import router as buildings_router

from .rooms_search_router import router as rooms_search_router
from .rooms_grid_router import router as rooms_grid_router
from .rooms_read_router import router as rooms_read_router
from .rooms_router import router as rooms_router

from .room_services_search_router import router as room_services_search_router
from .room_services_grid_router import router as room_services_grid_router
from .room_services_read_router import router as room_services_read_router
from .room_services_router import router as room_services_router

from .room_availabilities_search_router import router as room_availabilities_search_router
from .room_availabilities_grid_router import router as room_availabilities_grid_router
from .room_availabilities_read_router import router as room_availabilities_read_router
from .room_availabilities_router import router as room_availabilities_router

from .services_search_router import router as services_search_router
from .services_grid_router import router as services_grid_router
from .services_read_router import router as services_read_router
from .services_router import router as services_router

from .service_types_search_router import router as service_types_search_router
from .service_types_grid_router import router as service_types_grid_router
from .service_types_read_router import router as service_types_read_router
from .service_types_router import router as service_types_router


# ✅ Facade router (module-level)
router = APIRouter(prefix="/masters", tags=["Core_Settings"])

# include routers
router.include_router(companies_search_router, prefix="/companies")
router.include_router(companies_grid_router, prefix="/companies")
router.include_router(companies_read_router, prefix="/companies")
router.include_router(companies_router, prefix="/companies")

router.include_router(countries_search_router, prefix="/countries")
router.include_router(countries_grid_router, prefix="/countries")
router.include_router(countries_read_router, prefix="/countries")
router.include_router(countries_router, prefix="/countries")

router.include_router(currencies_search_router, prefix="/currencies")
router.include_router(currencies_grid_router, prefix="/currencies")
router.include_router(geographies_search_router, prefix="/geographies")
router.include_router(geographies_grid_router, prefix="/geographies")
router.include_router(languages_search_router, prefix="/languages")
router.include_router(languages_grid_router, prefix="/languages")

router.include_router(provinces_search_router, prefix="/provinces")
router.include_router(provinces_grid_router, prefix="/provinces")
router.include_router(provinces_read_router, prefix="/provinces")
router.include_router(provinces_router, prefix="/provinces")

router.include_router(cities_search_router, prefix="/cities")
router.include_router(cities_grid_router, prefix="/cities")
router.include_router(cities_read_router, prefix="/cities")
router.include_router(cities_router, prefix="/cities")

router.include_router(districts_search_router, prefix="/districts")
router.include_router(districts_grid_router, prefix="/districts")
router.include_router(districts_read_router, prefix="/districts")
router.include_router(districts_router, prefix="/districts")

router.include_router(departments_search_router, prefix="/departments")
router.include_router(departments_grid_router, prefix="/departments")
router.include_router(departments_read_router, prefix="/departments")
router.include_router(departments_router, prefix="/departments")

router.include_router(locations_search_router, prefix="/locations")
router.include_router(locations_grid_router, prefix="/locations")
router.include_router(locations_read_router, prefix="/locations")
router.include_router(locations_router, prefix="/locations")

router.include_router(buildings_search_router, prefix="/buildings")
router.include_router(buildings_grid_router, prefix="/buildings")
router.include_router(buildings_read_router, prefix="/buildings")
router.include_router(buildings_router, prefix="/buildings")

router.include_router(rooms_search_router, prefix="/rooms")
router.include_router(rooms_grid_router, prefix="/rooms")
router.include_router(rooms_read_router, prefix="/rooms")
router.include_router(rooms_router, prefix="/rooms")

router.include_router(room_services_search_router, prefix="/room_services")
router.include_router(room_services_grid_router, prefix="/room_services")
router.include_router(room_services_read_router, prefix="/room_services")
router.include_router(room_services_router, prefix="/room_services")

router.include_router(room_availabilities_search_router, prefix="/room_availabilities")
router.include_router(room_availabilities_grid_router, prefix="/room_availabilities")
router.include_router(room_availabilities_read_router, prefix="/room_availabilities")
router.include_router(room_availabilities_router, prefix="/room_availabilities")

router.include_router(services_search_router, prefix="/services")
router.include_router(services_grid_router, prefix="/services")
router.include_router(services_read_router, prefix="/services")
router.include_router(services_router, prefix="/services")

router.include_router(service_types_search_router, prefix="/service_types")
router.include_router(service_types_grid_router, prefix="/service_types")
router.include_router(service_types_read_router, prefix="/service_types")
router.include_router(service_types_router, prefix="/service_types")
