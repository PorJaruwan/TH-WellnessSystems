from __future__ import annotations

from app.api.v1.modules.doctor_dashboard.repositories.doctor_dashboard_action_repository import (
    DoctorDashboardActionRepository,
)


class DoctorDashboardActionService:
    def __init__(self, repository: DoctorDashboardActionRepository):
        self.repository = repository

    async def accept_booking(self, booking_id, **kwargs):
        booking = await self.repository.get_booking_for_update(booking_id)
        return await self.repository.accept_booking(booking, **kwargs)

    async def reject_booking(self, booking_id, **kwargs):
        booking = await self.repository.get_booking_for_update(booking_id)
        return await self.repository.reject_booking(booking, **kwargs)

    async def start_consultation(self, booking_id, **kwargs):
        booking = await self.repository.get_booking_for_update(booking_id)
        return await self.repository.start_consultation(booking, **kwargs)

    async def reschedule_booking(self, booking_id, **kwargs):
        booking = await self.repository.get_booking_for_update(booking_id)
        return await self.repository.reschedule_booking(booking, **kwargs)

    async def update_note_status(self, booking_id, **kwargs):
        booking = await self.repository.get_booking_for_update(booking_id)
        return await self.repository.update_note_status(booking, **kwargs)