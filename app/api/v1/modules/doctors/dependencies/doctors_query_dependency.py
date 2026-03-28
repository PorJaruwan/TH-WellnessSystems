from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.doctors.repositories.doctors_query_repository import (
    DoctorsQueryRepository,
)
from app.api.v1.modules.doctors.services.doctors_query_service import (
    DoctorsQueryService,
)

# from app.core.db import get_db
from app.database.session import get_db


def get_doctors_query_repository(
    db: AsyncSession = Depends(get_db),
) -> DoctorsQueryRepository:
    return DoctorsQueryRepository(db=db)


def get_doctors_query_service(
    repository: DoctorsQueryRepository = Depends(get_doctors_query_repository),
) -> DoctorsQueryService:
    return DoctorsQueryService(repository=repository)