# app/api/v1/modules/ai/consult/repositories/ai_consult_sessions_repository.py

from __future__ import annotations

import uuid
from typing import Optional, Sequence, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.chat.models.chat_models import ChatSession


def _to_uuid(v: str | uuid.UUID) -> uuid.UUID:
    if isinstance(v, uuid.UUID):
        return v
    return uuid.UUID(str(v))


class AIConsultSessionsRepository:
    """DB access layer for AI consult sessions (masters-style)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_patient_sessions(
        self,
        *,
        company_code: str,
        patient_id: str,
        status: str = "active",
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[Sequence[ChatSession], int]:
        pid = _to_uuid(patient_id)
        st = (status or "active").strip().lower()

        conds = [
            ChatSession.company_code == company_code,
            ChatSession.patient_id == pid,
            ChatSession.app_context == "ai_consult",
            ChatSession.channel == "patient",
        ]
        if st not in ("all", "*"):
            conds.append(ChatSession.status == ("closed" if st == "closed" else "active"))

        count_stmt = select(func.count()).select_from(ChatSession).where(*conds)
        total = (await self.db.execute(count_stmt)).scalar_one() or 0

        stmt = (
            select(ChatSession)
            .where(*conds)
            .order_by(func.coalesce(ChatSession.last_activity_at, ChatSession.created_at).desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all(), int(total)

    async def get_patient_session(
        self,
        *,
        company_code: str,
        patient_id: str,
        session_id: uuid.UUID,
    ) -> Optional[ChatSession]:
        pid = _to_uuid(patient_id)

        stmt = (
            select(ChatSession)
            .where(
                ChatSession.company_code == company_code,
                ChatSession.patient_id == pid,
                ChatSession.id == session_id,
                ChatSession.app_context == "ai_consult",
                ChatSession.channel == "patient",
            )
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalars().one_or_none()
