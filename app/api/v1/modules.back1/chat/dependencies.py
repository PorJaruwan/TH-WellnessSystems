from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

from app.api.v1.modules.chat.repositories.chat_repository import ChatRepository
from app.api.v1.modules.chat.services.chat_service import ChatService
from app.api.v1.modules.chat.services.chat_escalations_service import ChatEscalationsService
from app.api.v1.modules.chat.services.chat_retrievals_service import ChatRetrievalsService


def get_chat_repository(db: AsyncSession = Depends(get_db)) -> ChatRepository:
    return ChatRepository(db)


def get_chat_service(repo: ChatRepository = Depends(get_chat_repository)) -> ChatService:
    return ChatService(repo)


def get_chat_escalations_service(db: AsyncSession = Depends(get_db)) -> ChatEscalationsService:
    # masters-style DI: db injected once
    return ChatEscalationsService(db)


def get_chat_retrievals_service(db: AsyncSession = Depends(get_db)) -> ChatRetrievalsService:
    # masters-style DI: db injected once
    return ChatRetrievalsService(db)
