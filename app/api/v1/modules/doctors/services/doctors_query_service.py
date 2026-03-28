from __future__ import annotations

import json
from typing import Any

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

    async def get_doctors_by_service(
        self,
        params: DoctorByServiceQueryParams,
    ) -> DoctorByServiceListResponse:
        rows = await self.repository.get_doctors_by_service(params=params)

        items: list[DoctorByServiceItemResponse] = []
        for row in rows:
            raw_locations = self._normalize_locations(row.get("locations"))

            locations = [
                DoctorLocationResponse(
                    location_id=loc["location_id"],
                    location_name=loc["location_name"],
                )
                for loc in raw_locations
                if isinstance(loc, dict)
                and loc.get("location_id") is not None
                and loc.get("location_name") is not None
            ]

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
                    duration_minutes=row["duration_minutes"],
                    locations=locations,
                )
            )

        return DoctorByServiceListResponse(
            items=items,
            total=len(items),
        )