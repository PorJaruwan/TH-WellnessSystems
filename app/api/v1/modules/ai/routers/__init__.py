from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.modules.ai.consult.routers import router as consult_router

router = APIRouter(prefix="/ai", tags=["AI_Consult"])
router.include_router(consult_router)

__all__ = ["router"]