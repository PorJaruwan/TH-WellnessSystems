# Masters module - Full patients-style refactor

## What changed
- routers split per resource into:
  - *_search_router.py  (GET /{resource}/search)
  - *_read_router.py    (GET /{resource}/{id})
  - *_router.py         (POST/PUT/PATCH/DELETE)
- new layers:
  - repositories/ (DB-only, no commit/rollback)
  - services/     (transaction boundary)
  - models/dtos.py and models/_envelopes/

Legacy routers are kept at `routers/legacy/`.

## Required patch in app/api/v1/routers.py

Replace the "Core Settings" block with facade imports:

```python
from app.api.v1.modules.masters.routers import (
    companies_search_router, companies_read_router, companies_router,
    departments_search_router, departments_read_router, departments_router,
    locations_search_router, locations_read_router, locations_router,
    buildings_search_router, buildings_read_router, buildings_router,
    rooms_search_router, rooms_read_router, rooms_router,
    room_services_search_router, room_services_read_router, room_services_router,
    room_availabilities_search_router, room_availabilities_read_router, room_availabilities_router,
    services_search_router, services_read_router, services_router,
    service_types_search_router, service_types_read_router, service_types_router,
    countries_search_router, countries_read_router, countries_router,
    provinces_search_router, provinces_read_router, provinces_router,
    cities_search_router, cities_read_router, cities_router,
    districts_search_router, districts_read_router, districts_router,
    currencies_search_router,
    languages_search_router,
    geographies_search_router,
)

api_router.include_router(companies_search_router)
api_router.include_router(companies_read_router)
api_router.include_router(companies_router)
# ...repeat include_router for the rest...
```

(You can also group includes per resource.)
