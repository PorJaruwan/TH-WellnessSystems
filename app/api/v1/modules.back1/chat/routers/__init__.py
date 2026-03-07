from __future__ import annotations

from fastapi import APIRouter

from .chat_sessions_search_router import router as chat_sessions_search_router
from .chat_sessions_read_router import router as chat_sessions_read_router
from .chat_sessions_router import router as chat_sessions_router

from .chat_escalations_search_router import router as chat_escalations_search_router
from .chat_escalations_router import router as chat_escalations_router

from .chat_retrievals_search_router import router as chat_retrievals_search_router
from .chat_retrievals_read_router import router as chat_retrievals_read_router
from .chat_retrievals_router import router as chat_retrievals_router

# Messages
from .chat_messages_router import router as chat_messages_router


# Facade Router (single source of truth)
router = APIRouter(prefix="/chat", tags=["Chat"])

# Sessions: /chat/sessions/...
router.include_router(chat_sessions_search_router, prefix="/sessions")
router.include_router(chat_sessions_read_router, prefix="/sessions")
router.include_router(chat_sessions_router, prefix="/sessions")

# Messages: /chat/messages/...
router.include_router(chat_messages_router, prefix="/messages")

# Escalations: /chat/escalations/...
router.include_router(chat_escalations_search_router, prefix="/escalations")
router.include_router(chat_escalations_router, prefix="/escalations")

# Retrievals list is nested under sessions: /chat/sessions/{session_id}/retrievals
router.include_router(chat_retrievals_search_router, prefix="/sessions")

# Retrievals (internal): /chat/retrievals/...
router.include_router(chat_retrievals_read_router, prefix="/retrievals")
router.include_router(chat_retrievals_router, prefix="/retrievals")


__all__ = ["router"]
