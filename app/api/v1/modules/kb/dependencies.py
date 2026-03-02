from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.v1.authen.auth import current_company_code
from app.core.config import get_settings, Settings

from .repositories.kb_documents_repository import KBDocumentsRepository
from .repositories.kb_chunks_repository import KBChunksRepository
from .repositories.kb_search_repository import KBSearchRepository

from .services.kb_documents_service import KBDocumentsService
from .services.kb_chunks_service import KBChunksService
from .services.kb_search_service import KBSearchService


def get_kb_documents_repository(db: AsyncSession = Depends(get_db)) -> KBDocumentsRepository:
    return KBDocumentsRepository(db)


def get_kb_chunks_repository(db: AsyncSession = Depends(get_db)) -> KBChunksRepository:
    return KBChunksRepository(db)


def get_kb_search_repository(db: AsyncSession = Depends(get_db)) -> KBSearchRepository:
    return KBSearchRepository(db)


def get_kb_documents_service(
    repo: KBDocumentsRepository = Depends(get_kb_documents_repository),
    company_code: str = Depends(current_company_code),
) -> KBDocumentsService:
    return KBDocumentsService(repo=repo, company_code=company_code)


def get_kb_chunks_service(
    repo: KBChunksRepository = Depends(get_kb_chunks_repository),
    company_code: str = Depends(current_company_code),
) -> KBChunksService:
    return KBChunksService(repo=repo, company_code=company_code)


def get_kb_search_service(
    repo: KBSearchRepository = Depends(get_kb_search_repository),
    company_code: str = Depends(current_company_code),
    settings: Settings = Depends(get_settings),
) -> KBSearchService:
    return KBSearchService(repo=repo, company_code=company_code, settings=settings)
