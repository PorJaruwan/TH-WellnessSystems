from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from app.api.v1.modules.doctors.repositories.doctors_query_repository import (
    DoctorsQueryRepository,
)
from app.api.v1.modules.doctors.schemas.doctors_query_params import (
    DoctorByServiceQueryParams,
)
from app.api.v1.modules.doctors.schemas.doctors_query_response import (
    DoctorByServiceItemResponse,
    DoctorByServiceListResponse,
    DoctorLocationResponse,
)


class DoctorsQueryService:
    def __init__(self, repository: DoctorsQueryRepository):
        self.repository = repository

    @staticmethod
    def _normalize_locations(raw_locations: Any) -> list[dict]:
        if raw_locations is None:
            return []

        if isinstance(raw_locations, str):
            try:
                parsed = json.loads(raw_locations)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                return []

        if isinstance(raw_locations, list):
            return raw_locations

        return []

    @staticmethod
    def _normalize_uuid(value: Any) -> UUID | None:
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        try:
            return UUID(str(value))
        except (ValueError, TypeError):
            return None

    async def get_doctors_by_service(
        self,
        params: DoctorByServiceQueryParams,
    ) -> DoctorByServiceListResponse:
        rows = await self.repository.get_doctors_by_service(params=params)

        items: list[DoctorByServiceItemResponse] = []

        for row in rows:
            raw_locations = self._normalize_locations(row.get("locations"))

            locations: list[DoctorLocationResponse] = []
            seen_location_ids: set[str] = set()

            for loc in raw_locations:
                if not isinstance(loc, dict):
                    continue

                normalized_location_id = self._normalize_uuid(loc.get("location_id"))
                location_name = loc.get("location_name")

                if normalized_location_id is None or not location_name:
                    continue

                location_key = str(normalized_location_id)
                if location_key in seen_location_ids:
                    continue

                seen_location_ids.add(location_key)

                locations.append(
                    DoctorLocationResponse(
                        location_id=normalized_location_id,
                        location_name=location_name,
                    )
                )

            duration_minutes = row.get("duration_minutes")
            if duration_minutes is None:
                duration_minutes = 0

            items.append(
                DoctorByServiceItemResponse(
                    doctor_id=row["doctor_id"],
                    staff_name=row["staff_name"],
                    role=row["role"],
                    license_number=row.get("license_number"),
                    specialty=row.get("specialty"),
                    gender=row.get("gender"),
                    phone=row.get("phone"),
                    email=row.get("email"),
                    avatar_url=row.get("avatar_url"),
                    main_location_id=row.get("main_location_id"),
                    service_id=row["service_id"],
                    service_code=row.get("service_code"),
                    service_name=row["service_name"],
                    service_name_th=row.get("service_name_th"),
                    service_name_en=row.get("service_name_en"),
                    duration_minutes=int(duration_minutes),
                    locations=locations,
                )
            )

        return DoctorByServiceListResponse(
            items=items,
            total=len(items),
        )