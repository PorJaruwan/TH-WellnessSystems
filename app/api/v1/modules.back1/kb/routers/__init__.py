from __future__ import annotations

from fastapi import APIRouter

from .kb_documents_router import router as kb_documents_router
from .kb_chunks_router import router as kb_chunks_router
from .kb_search_router import router as kb_search_router

router = APIRouter(prefix="/kb", tags=["KB"])

# include sub-routers (ไม่ import ตัวเอง!)
router.include_router(kb_search_router)
router.include_router(kb_documents_router, prefix="/documents")
router.include_router(kb_chunks_router, prefix="/documents")


__all__ = ["router"]