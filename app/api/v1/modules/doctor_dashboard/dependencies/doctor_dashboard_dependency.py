from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.doctor_dashboard.repositories.doctor_dashboard_query_repository import (
    DoctorDashboardQueryRepository,
)
from app.api.v1.modules.doctor_dashboard.services.doctor_dashboard_query_service import (
    DoctorDashboardQueryService,
)
from app.database.session import get_db


def get_doctor_dashboard_query_repository(
    db: AsyncSession = Depends(get_db),
) -> DoctorDashboardQueryRepository:
    return DoctorDashboardQueryRepository(db=db)


def get_doctor_dashboard_query_service(
    repository: DoctorDashboardQueryRepository = Depends(
        get_doctor_dashboard_query_repository
    ),
) -> DoctorDashboardQueryService:
    return DoctorDashboardQueryService(repository=repository)