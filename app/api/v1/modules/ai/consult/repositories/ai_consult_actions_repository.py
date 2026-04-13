from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.chat.models.chat_models import ChatSession, ChatMessage
from app.api.v1.modules.ai.consult.services.ai_consult_service import _to_uuid


class AIConsultActionsRepository:
    """
    Repository for AI consult quick actions.
    Owns DB read/write operations related to session + assistant message persistence.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_owned_session(
        self,
        *,
        company_code: str,
        patient_id: str,
        session_id: UUID | str,
    ) -> Optional[ChatSession]:
        sid = _to_uuid(session_id)
        pid = _to_uuid(patient_id)

        q = select(ChatSession).where(
            ChatSession.id == sid,
            ChatSession.company_code == company_code,
            ChatSession.patient_id == pid,
        )
        return (await self.db.execute(q)).scalar_one_or_none()

    async def add_assistant_message(
        self,
        *,
        company_code: str,
        session_id: UUID | str,
        topic_code: str,
        action: str,
        items: list[str],
        disclaimer: str,
        assistant_text: str,
        triage: dict[str, Any],
        ui_cards: list[dict[str, Any]],
    ) -> ChatMessage:
        sid = _to_uuid(session_id)

        msg = ChatMessage(
            company_code=company_code,
            session_id=sid,
            role="assistant",
            content=assistant_text,
            content_json={
                "quick_action": action,
                "topic_code": topic_code,
                "items": items,
                "disclaimer": disclaimer,
                "triage": triage,
                "ui_cards": ui_cards,
                "retrieval": None,
                "source": "ai_topics.default_cards",
            },
        )
        self.db.add(msg)
        return msg

    async def set_session_triage(
        self,
        *,
        session: ChatSession,
        triage: dict[str, Any],
    ) -> None:
        session.triage_level = triage.get("level")
        session.triage_reason = triage.get("reason")

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()