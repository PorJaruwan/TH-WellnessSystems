from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.doctor_dashboard.schemas.doctor_dashboard_query_params import (
    DoctorDashboardInboxBookingByIdQueryParams,
    DoctorDashboardInboxQueryParams,
    DoctorDashboardInboxSummaryQueryParams,
)


class DoctorDashboardQueryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _build_common_filters(
        *,
        params: Any,
        include_patient_id: bool = True,
    ) -> tuple[list[str], Dict[str, Any]]:
        filters: list[str] = ["1=1"]

        query_params: Dict[str, Any] = {
            "company_code": params.company_code,
            "location_id": str(params.location_id) if getattr(params, "location_id", None) else None,
            "building_id": str(params.building_id) if getattr(params, "building_id", None) else None,
            "room_id": str(params.room_id) if getattr(params, "room_id", None) else None,
            "patient_id": str(params.patient_id) if include_patient_id and getattr(params, "patient_id", None) else None,
            "primary_person_id": str(params.primary_person_id) if getattr(params, "primary_person_id", None) else None,
            "booking_date": params.booking_date,
            "status": getattr(params, "status", None),
            "consultation_type": getattr(params, "consultation_type", None),
            "note_status": getattr(params, "note_status", None),
        }

        if params.company_code:
            filters.append("b.company_code = :company_code")

        if getattr(params, "location_id", None):
            filters.append("b.location_id = CAST(:location_id AS uuid)")

        if getattr(params, "building_id", None):
            filters.append("b.building_id = CAST(:building_id AS uuid)")

        if getattr(params, "room_id", None):
            filters.append("b.room_id = CAST(:room_id AS uuid)")

        if include_patient_id and getattr(params, "patient_id", None):
            filters.append("b.patient_id = CAST(:patient_id AS uuid)")

        if getattr(params, "primary_person_id", None):
            filters.append("b.primary_person_id = CAST(:primary_person_id AS uuid)")

        if getattr(params, "booking_date", None):
            filters.append("b.booking_date = :booking_date")

        if getattr(params, "status", None):
            filters.append("b.status = :status")

        if getattr(params, "consultation_type", None):
            filters.append("b.consultation_type = :consultation_type")

        if getattr(params, "note_status", None):
            filters.append("b.note_status = :note_status")

        return filters, query_params

    @staticmethod
    def _build_search_filter(
        q: Optional[str],
        query_params: Dict[str, Any],
    ) -> Optional[str]:
        if not q:
            return None

        normalized_q = q.strip()
        if not normalized_q:
            return None

        query_params["q"] = f"%{normalized_q}%"

        return """
        (
            p.full_name_lo ILIKE :q
            OR COALESCE(p.full_name_en, '') ILIKE :q
            OR p.patient_code ILIKE :q
            OR l.location_name ILIKE :q
            OR COALESCE(l.location_code, '') ILIKE :q
        )
        """

    @staticmethod
    def _resolve_order_by(sort_by: str, sort_dir: str) -> str:
        direction = "DESC" if sort_dir.lower() == "desc" else "ASC"

        mapping = {
            "booking_date": f"b.booking_date {direction}, b.start_time {direction}",
            "start_time": f"b.start_time {direction}, b.booking_date {direction}",
            "end_time": f"b.end_time {direction}, b.booking_date {direction}",
            "status": f"b.status {direction}, b.start_time ASC",
            "consultation_type": f"b.consultation_type {direction}, b.start_time ASC",
            "note_status": f"b.note_status {direction}, b.start_time ASC",
            "patient_name": f"p.full_name_lo {direction}, p.patient_code ASC",
            "patient_code": f"p.patient_code {direction}, p.full_name_lo ASC",
            "location_name": f"l.location_name {direction}, b.start_time ASC",
            "staff_name": f"st.staff_name {direction}, b.start_time ASC",
            "service_name": f"s.service_name {direction}, b.start_time ASC",
        }

        return mapping.get("start_time" if sort_by not in mapping else sort_by, mapping["start_time"])

    async def search_inbox(
        self,
        params: DoctorDashboardInboxQueryParams,
    ) -> dict[str, Any]:
        filters, query_params = self._build_common_filters(params=params, include_patient_id=True)

        search_filter = self._build_search_filter(params.q, query_params)
        if search_filter:
            filters.append(search_filter)

        query_params["limit"] = params.limit
        query_params["offset"] = params.offset

        where_clause = " AND ".join(filters)
        order_by_clause = self._resolve_order_by(params.sort_by, params.sort_dir)

        sql = text(
            f"""
            SELECT
                b.id AS booking_id,
                b.company_code,

                b.location_id,
                l.location_name,
                l.location_code,

                b.building_id,
                bd.building_name,
                bd.building_code,

                b.room_id,
                r.room_name,
                r.room_code,

                b.patient_id,
                p.full_name_lo,
                p.full_name_en,
                p.patient_code,

                b.service_id,
                s.service_name,
                s.service_code,

                b.primary_person_id,
                st.staff_name,
                st.role,

                b.booking_date,
                b.note,
                b.start_time,
                b.end_time,
                b.status,
                b.consultation_type,
                b.note_status

            FROM bookings b
            JOIN locations l
                ON l.id = b.location_id
            JOIN buildings bd
                ON bd.id = b.building_id
            JOIN rooms r
                ON r.id = b.room_id
            JOIN patients p
                ON p.id = b.patient_id
            JOIN services s
                ON s.id = b.service_id
            JOIN staff st
                ON st.id = b.primary_person_id

            WHERE {where_clause}

            ORDER BY {order_by_clause}
            LIMIT :limit
            OFFSET :offset
            """
        )

        count_sql = text(
            f"""
            SELECT COUNT(1) AS total
            FROM bookings b
            JOIN locations l
                ON l.id = b.location_id
            JOIN buildings bd
                ON bd.id = b.building_id
            JOIN rooms r
                ON r.id = b.room_id
            JOIN patients p
                ON p.id = b.patient_id
            JOIN services s
                ON s.id = b.service_id
            JOIN staff st
                ON st.id = b.primary_person_id
            WHERE {where_clause}
            """
        )

        result = await self.db.execute(sql, query_params)
        rows = result.mappings().all()

        count_result = await self.db.execute(count_sql, query_params)
        total = count_result.scalar_one() or 0

        return {
            "items": [dict(row) for row in rows],
            "total": int(total),
        }

    async def get_inbox_summary(
        self,
        params: DoctorDashboardInboxSummaryQueryParams,
    ) -> Dict[str, Any]:
        filters, query_params = self._build_common_filters(params=params, include_patient_id=False)

        where_clause = " AND ".join(filters)

        sql = text(
            f"""
            SELECT
                COUNT(1) AS total_all,

                SUM(CASE WHEN b.note_status = 'draft' THEN 1 ELSE 0 END) AS total_draft_note,
                SUM(CASE WHEN b.note_status = 'completed' THEN 1 ELSE 0 END) AS total_completed_note,
                SUM(CASE WHEN b.note_status = 'signed' THEN 1 ELSE 0 END) AS total_signed_note,

                SUM(CASE WHEN b.consultation_type = 'online' THEN 1 ELSE 0 END) AS total_online,
                SUM(CASE WHEN b.consultation_type = 'onsite' THEN 1 ELSE 0 END) AS total_onsite,

                SUM(CASE WHEN b.status = 'booked' THEN 1 ELSE 0 END) AS total_booked,
                SUM(CASE WHEN b.status = 'confirmed' THEN 1 ELSE 0 END) AS total_confirmed,
                SUM(CASE WHEN b.status = 'checked_in' THEN 1 ELSE 0 END) AS total_checked_in,
                SUM(CASE WHEN b.status = 'in_service' THEN 1 ELSE 0 END) AS total_in_service,
                SUM(CASE WHEN b.status = 'completed' THEN 1 ELSE 0 END) AS total_completed,
                SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) AS total_cancelled,
                SUM(CASE WHEN b.status = 'no_show' THEN 1 ELSE 0 END) AS total_no_show,
                SUM(CASE WHEN b.status = 'rescheduled' THEN 1 ELSE 0 END) AS total_rescheduled

            FROM bookings b
            WHERE {where_clause}
            """
        )

        result = await self.db.execute(sql, query_params)
        row = result.mappings().first()

        return dict(row) if row else {}

    async def get_inbox_booking_by_id(
        self,
        booking_id: UUID,
        params: DoctorDashboardInboxBookingByIdQueryParams,
    ) -> Dict[str, Any] | None:
        query_params: Dict[str, Any] = {
            "booking_id": str(booking_id),
            "company_code": params.company_code,
        }

        filters = [
            "b.id = CAST(:booking_id AS uuid)",
        ]

        if params.company_code:
            filters.append("b.company_code = :company_code")

        where_clause = " AND ".join(filters)

        sql = text(
            f"""
            SELECT
                b.id AS booking_id,
                b.company_code,

                b.location_id,
                l.location_name,
                l.location_code,

                b.building_id,
                bd.building_name,
                bd.building_code,

                b.room_id,
                r.room_name,
                r.room_code,

                b.patient_id,
                p.full_name_lo,
                p.full_name_en,
                p.patient_code,

                b.service_id,
                s.service_name,
                s.service_code,

                b.primary_person_id,
                st.staff_name,
                st.role,

                b.booking_date,
                b.note,
                b.start_time,
                b.end_time,
                b.status,
                b.consultation_type,
                b.note_status

            FROM bookings b
            JOIN locations l
                ON l.id = b.location_id
            JOIN buildings bd
                ON bd.id = b.building_id
            JOIN rooms r
                ON r.id = b.room_id
            JOIN patients p
                ON p.id = b.patient_id
            JOIN services s
                ON s.id = b.service_id
            JOIN staff st
                ON st.id = b.primary_person_id

            WHERE {where_clause}
            LIMIT 1
            """
        )

        result = await self.db.execute(sql, query_params)
        row = result.mappings().first()
        return dict(row) if row else None