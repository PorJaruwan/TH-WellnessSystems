from __future__ import annotations

from fastapi import APIRouter

from .ai_consult_router import router as ai_consult_router

router = APIRouter(prefix="/ai", tags=["AI Consult"])

router.include_router(ai_consult_router, prefix="/consult")

__all__ = ["router"]
