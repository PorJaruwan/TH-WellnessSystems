from __future__ import annotations

from uuid import UUID

from app.api.v1.modules.doctor_dashboard.repositories.doctor_dashboard_query_repository import (
    DoctorDashboardQueryRepository,
)
from app.api.v1.modules.doctor_dashboard.schemas.doctor_dashboard_query_params import (
    DoctorDashboardInboxBookingByIdQueryParams,
    DoctorDashboardInboxQueryParams,
    DoctorDashboardInboxSummaryQueryParams,
)
from app.api.v1.modules.doctor_dashboard.schemas.doctor_dashboard_query_response import (
    DoctorDashboardInboxBookingDetailResponse,
    DoctorDashboardInboxFiltersResponse,
    DoctorDashboardInboxItemResponse,
    DoctorDashboardInboxListResponse,
    DoctorDashboardInboxPagingResponse,
    DoctorDashboardInboxSortResponse,
    DoctorDashboardInboxSummaryResponse,
)


class DoctorDashboardQueryService:
    def __init__(self, repository: DoctorDashboardQueryRepository):
        self.repository = repository

    async def search_inbox(
        self,
        params: DoctorDashboardInboxQueryParams,
    ) -> DoctorDashboardInboxListResponse:
        result = await self.repository.search_inbox(params=params)

        items = [
            DoctorDashboardInboxItemResponse.model_validate(row)
            for row in result.get("items", [])
        ]

        return DoctorDashboardInboxListResponse(
            filters=DoctorDashboardInboxFiltersResponse(
                q=params.q,
                company_code=params.company_code,
                location_id=params.location_id,
                building_id=params.building_id,
                room_id=params.room_id,
                patient_id=params.patient_id,
                primary_person_id=params.primary_person_id,
                booking_date=params.booking_date,
                status=params.status,
                consultation_type=params.consultation_type,
                note_status=params.note_status,
            ),
            sort=DoctorDashboardInboxSortResponse(
                by=params.sort_by,
                order=params.sort_dir,
            ),
            paging=DoctorDashboardInboxPagingResponse(
                total=int(result.get("total", 0)),
                limit=params.limit,
                offset=params.offset,
            ),
            items=items,
        )

    async def get_inbox_summary(
        self,
        params: DoctorDashboardInboxSummaryQueryParams,
    ) -> DoctorDashboardInboxSummaryResponse:
        row = await self.repository.get_inbox_summary(params=params)

        return DoctorDashboardInboxSummaryResponse(
            total_all=int(row.get("total_all") or 0),
            total_draft_note=int(row.get("total_draft_note") or 0),
            total_completed_note=int(row.get("total_completed_note") or 0),
            total_signed_note=int(row.get("total_signed_note") or 0),
            total_online=int(row.get("total_online") or 0),
            total_onsite=int(row.get("total_onsite") or 0),
            total_booked=int(row.get("total_booked") or 0),
            total_confirmed=int(row.get("total_confirmed") or 0),
            total_checked_in=int(row.get("total_checked_in") or 0),
            total_in_service=int(row.get("total_in_service") or 0),
            total_completed=int(row.get("total_completed") or 0),
            total_cancelled=int(row.get("total_cancelled") or 0),
            total_no_show=int(row.get("total_no_show") or 0),
            total_rescheduled=int(row.get("total_rescheduled") or 0),
        )

    async def get_inbox_booking_by_id(
        self,
        booking_id: UUID,
        params: DoctorDashboardInboxBookingByIdQueryParams,
    ) -> DoctorDashboardInboxBookingDetailResponse | None:
        row = await self.repository.get_inbox_booking_by_id(
            booking_id=booking_id,
            params=params,
        )

        if not row:
            return None

        return DoctorDashboardInboxBookingDetailResponse.model_validate(row)