from __future__ import annotations

from fastapi import APIRouter

from .ai_consult_topics_router import router as topics_router
from .ai_consult_topic_categories_router import router as topic_categories_router
from .ai_consult_topic_services_router import router as topic_services_router
from .ai_consult_sessions_router import router as sessions_router
from .ai_consult_actions_router import router as actions_router
from .ai_consult_escalations_router import router as escalations_router



# ✅ Facade router (module-level)
router = APIRouter(prefix="/consult", tags=["AI_Consult"])

router.include_router(topics_router, prefix="/topics")
router.include_router(topic_categories_router, prefix="/topic-categories")
router.include_router(topic_services_router, prefix="/topic-services")
router.include_router(sessions_router, prefix="/sessions")
router.include_router(actions_router, prefix="/sessions")
router.include_router(escalations_router, prefix="/sessions")


__all__ = ["router"]
