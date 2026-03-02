from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.v1.modules.ai.consult.repositories.ai_consult_sessions_repository import AIConsultSessionsRepository
from app.api.v1.modules.ai.consult.services.ai_consult_sessions_service import AIConsultSessionsService


def get_ai_consult_sessions_repository(db: AsyncSession = Depends(get_db)) -> AIConsultSessionsRepository:
    return AIConsultSessionsRepository(db)


def get_ai_consult_sessions_service(
    repo: AIConsultSessionsRepository = Depends(get_ai_consult_sessions_repository),
) -> AIConsultSessionsService:
    return AIConsultSessionsService(repo)
