from sqlalchemy.ext.asyncio import AsyncSession


class DoctorDashboardActionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_booking_for_update(self, booking_id):
        raise NotImplementedError

    async def accept_booking(self, booking, **kwargs):
        raise NotImplementedError

    async def reject_booking(self, booking, **kwargs):
        raise NotImplementedError

    async def start_consultation(self, booking, **kwargs):
        raise NotImplementedError

    async def reschedule_booking(self, booking, **kwargs):
        raise NotImplementedError

    async def update_note_status(self, booking, **kwargs):
        raise NotImplementedError