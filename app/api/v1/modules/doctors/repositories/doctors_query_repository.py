from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.doctors.schemas.doctors_query_params import (
    DoctorByServiceQueryParams,
)


class DoctorsQueryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_doctors_by_service(
        self,
        params: DoctorByServiceQueryParams,
    ) -> List[Dict[str, Any]]:
        filters = [
            "st.is_active = true",
            "LOWER(st.role) = 'doctor'",
            "sd.is_active = true",
            "svd.is_active = true",
            "s.is_active = true",
        ]

        query_params: Dict[str, Any] = {
            "service_id": str(params.service_id) if params.service_id else None,
            "service_code": params.service_code,
            "location_id": str(params.location_id) if params.location_id else None,
            "company_code": params.company_code,
        }

        if params.service_id:
            filters.append("s.id = CAST(:service_id AS uuid)")
        else:
            filters.append("s.service_code = :service_code")
            filters.append("s.company_code = :company_code")

        if params.company_code:
            filters.append("s.company_code = :company_code")

        if params.location_id:
            filters.append("l.id = CAST(:location_id AS uuid)")

        if params.primary_only:
            filters.append("sl.is_primary = true")

        where_clause = " AND ".join(filters)

        location_join = """
            LEFT JOIN locations l
                ON l.id = sl.location_id
               AND l.is_active = true
        """

        if params.company_code:
            location_join = """
                LEFT JOIN locations l
                    ON l.id = sl.location_id
                   AND l.is_active = true
                   AND l.company_code = :company_code
            """

        sql = text(f"""
            SELECT
                st.id AS doctor_id,
                st.staff_name,
                st.role,
                st.license_number,
                st.specialty,
                st.gender,
                st.phone,
                st.email,
                st.avatar_url,
                st.main_location_id,

                s.id AS service_id,
                s.service_code,
                s.service_name,
                s.service_name_th,
                s.service_name_en,
                s.duration AS duration_minutes,

                COALESCE(
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'location_id', l.id,
                            'location_name', l.location_name
                        )
                    ) FILTER (WHERE l.id IS NOT NULL),
                    '[]'::json
                ) AS locations

            FROM staff st
            JOIN staff_departments sd
                ON sd.staff_id = st.id
               AND sd.is_active = true
            JOIN services_departments svd
                ON svd.department_id = sd.department_id
               AND svd.is_active = true
            JOIN services s
                ON s.id = svd.service_id
               AND s.is_active = true
            LEFT JOIN staff_locations sl
                ON sl.staff_id = st.id
               AND sl.is_active = true
            {location_join}

            WHERE {where_clause}

            GROUP BY
                st.id,
                st.staff_name,
                st.role,
                st.license_number,
                st.specialty,
                st.gender,
                st.phone,
                st.email,
                st.avatar_url,
                st.main_location_id,
                s.id,
                s.service_code,
                s.service_name,
                s.service_name_th,
                s.service_name_en,
                s.duration

            ORDER BY
                st.staff_name ASC,
                s.service_name ASC
        """)

        result = await self.db.execute(sql, query_params)
        rows = result.mappings().all()
        return [dict(row) for row in rows]