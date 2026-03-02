# app/api/v1/modules/chat/repositories/chat_repository.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Select, select, update, text, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.chat.models.chat_models import ChatSession, ChatMessage


@dataclass
class ChatSessionHeaderDTO:
    session_id: UUID
    status: str
    title: Optional[str]
    topic_code: Optional[str]
    language: Optional[str]
    triage_level: Optional[str]
    triage_reason: Optional[str]
    last_activity_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ChatRepository:
    """
    - Repository: no commit/rollback
    - Service: handles commit/rollback
    """

    # =========================
    # Sessions
    # =========================
    @staticmethod
    async def create_patient_session(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        topic_code: Optional[str] = None,
        language: str = "th-TH",
        channel: str = "flutterflow",
        app_context: str = "patient",
    ) -> ChatSession:
        s = ChatSession(
            company_code=company_code,
            patient_id=patient_id,
            staff_id=None,
            app_context=app_context,
            channel=channel,
            status="open",
            topic_code=topic_code,
            language=language,
            last_activity_at=datetime.utcnow(),
        )
        db.add(s)
        await db.flush()
        await db.refresh(s)
        return s

    @staticmethod
    async def get_owned_session(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
    ) -> Optional[ChatSession]:
        stmt = select(ChatSession).where(
            ChatSession.company_code == company_code,
            ChatSession.id == session_id,
            ChatSession.patient_id == patient_id,
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def get_session_header(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
    ) -> Optional[ChatSessionHeaderDTO]:
        s = await ChatRepository.get_owned_session(
            db,
            company_code=company_code,
            patient_id=patient_id,
            session_id=session_id,
        )
        if not s:
            return None

        return ChatSessionHeaderDTO(
            session_id=s.id,
            status=getattr(s, "status", None),
            title=getattr(s, "title", None),
            topic_code=getattr(s, "topic_code", None),
            language=getattr(s, "language", None),
            triage_level=getattr(s, "triage_level", None),
            triage_reason=getattr(s, "triage_reason", None),
            last_activity_at=getattr(s, "last_activity_at", None),
            created_at=getattr(s, "created_at", None),
            updated_at=getattr(s, "updated_at", None),
        )

    @staticmethod
    async def close_session(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
    ) -> Optional[ChatSessionHeaderDTO]:
        s = await ChatRepository.get_owned_session(
            db,
            company_code=company_code,
            patient_id=patient_id,
            session_id=session_id,
        )
        if not s:
            return None

        s.status = "closed"
        s.last_activity_at = datetime.utcnow()
        await db.flush()
        await db.refresh(s)

        return ChatSessionHeaderDTO(
            session_id=s.id,
            status=s.status,
            title=getattr(s, "title", None),
            topic_code=getattr(s, "topic_code", None),
            language=getattr(s, "language", None),
            triage_level=getattr(s, "triage_level", None),
            triage_reason=getattr(s, "triage_reason", None),
            last_activity_at=getattr(s, "last_activity_at", None),
            created_at=getattr(s, "created_at", None),
            updated_at=getattr(s, "updated_at", None),
        )

    @staticmethod
    async def reopen_session(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
    ) -> Optional[ChatSessionHeaderDTO]:
        s = await ChatRepository.get_owned_session(
            db,
            company_code=company_code,
            patient_id=patient_id,
            session_id=session_id,
        )
        if not s:
            return None

        s.status = "open"
        s.last_activity_at = datetime.utcnow()
        await db.flush()
        await db.refresh(s)

        return ChatSessionHeaderDTO(
            session_id=s.id,
            status=s.status,
            title=getattr(s, "title", None),
            topic_code=getattr(s, "topic_code", None),
            language=getattr(s, "language", None),
            triage_level=getattr(s, "triage_level", None),
            triage_reason=getattr(s, "triage_reason", None),
            last_activity_at=getattr(s, "last_activity_at", None),
            created_at=getattr(s, "created_at", None),
            updated_at=getattr(s, "updated_at", None),
        )

    @staticmethod
    async def list_my_sessions_summary(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        status: str = "open",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Updated rule (now that vw has last_activity_at):
        - If view exists -> query it ORDER BY last_activity_at
        - Else -> query chat_sessions ORDER BY chat_sessions.last_activity_at
        NOTE: Do not attempt multiple failing queries inside one request.
        """

        chk = await db.execute(text("SELECT to_regclass('public.vw_chat_sessions_summary')"))
        view_name = chk.scalar_one_or_none()

        if view_name:
            base_where = """
                FROM public.vw_chat_sessions_summary
                WHERE company_code = :cc
                  AND patient_id = :pid
                  AND status = :st
            """

            count_stmt = text("SELECT COUNT(1) " + base_where)
            total = (
                await db.execute(
                    count_stmt,
                    {"cc": company_code, "pid": str(patient_id), "st": status},
                )
            ).scalar_one() or 0

            data_stmt = text(
                """
                SELECT *
                """ + base_where + """
                ORDER BY last_activity_at DESC NULLS LAST
                LIMIT :lim OFFSET :off
                """
            )
            res = await db.execute(
                data_stmt,
                {"cc": company_code, "pid": str(patient_id), "st": status, "lim": limit, "off": offset},
            )
            return [dict(r) for r in res.mappings().all()], int(total)

        # Fallback to base table
        total_stmt2 = select(func.count()).select_from(ChatSession).where(
            ChatSession.company_code == company_code,
            ChatSession.patient_id == patient_id,
            ChatSession.status == status,
        )
        total2 = (await db.execute(total_stmt2)).scalar_one() or 0

        stmt2 = (
            select(ChatSession)
            .where(
                ChatSession.company_code == company_code,
                ChatSession.patient_id == patient_id,
                ChatSession.status == status,
            )
            .order_by(desc(ChatSession.last_activity_at))
            .limit(limit)
            .offset(offset)
        )
        res2 = await db.execute(stmt2)
        sessions = res2.scalars().all()

        return [
            {
                "session_id": s.id,
                "status": s.status,
                "title": getattr(s, "title", None),
                "topic_code": getattr(s, "topic_code", None),
                "created_at": getattr(s, "created_at", None),
                "last_activity_at": getattr(s, "last_activity_at", None),
            }
            for s in sessions
        ], int(total2)

    # =========================
    # Messages
    # =========================
    @staticmethod
    async def list_messages(
        db: AsyncSession,
        *,
        company_code: str,
        session_id: UUID,
        limit: int = 50,
        offset: int = 0,
        before: Optional[datetime] = None,
    ) -> tuple[list[ChatMessage], int]:
        conditions = [
            ChatMessage.company_code == company_code,
            ChatMessage.session_id == session_id,
        ]
        stmt: Select = select(ChatMessage).where(*conditions)

        if hasattr(ChatMessage, "is_deleted"):
            conditions.append(ChatMessage.is_deleted.is_(False))  # type: ignore[attr-defined]
            stmt = stmt.where(ChatMessage.is_deleted.is_(False))  # type: ignore[attr-defined]

        if before is not None:
            conditions.append(ChatMessage.created_at < before)
            stmt = stmt.where(ChatMessage.created_at < before)

        total_stmt = select(func.count()).select_from(ChatMessage).where(*conditions)
        total = (await db.execute(total_stmt)).scalar_one() or 0

        stmt = stmt.order_by(desc(ChatMessage.created_at)).limit(limit).offset(offset)

        res = await db.execute(stmt)
        return res.scalars().all(), int(total)

    @staticmethod
    async def insert_message(
        db: AsyncSession,
        *,
        company_code: str,
        session_id: UUID,
        role: str,
        content: str,
        content_json: dict[str, Any],
    ) -> ChatMessage:
        """
        NOTE:
        - If the session update fails, raise (do not swallow), so Service can rollback.
        - Swallowing can leave transaction aborted and break subsequent operations.
        """
        m = ChatMessage(
            company_code=company_code,
            session_id=session_id,
            role=role,
            content=content,
            content_json=content_json,
        )
        db.add(m)

        # Keep session activity in sync (must not silently abort tx)
        stmt = (
            update(ChatSession)
            .where(ChatSession.id == session_id, ChatSession.company_code == company_code)
            .values(last_activity_at=datetime.utcnow())
        )
        await db.execute(stmt)

        await db.flush()
        await db.refresh(m)
        return m

    @staticmethod
    async def soft_delete_message(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        message_id: UUID,
    ) -> bool:
        stmt_find = (
            select(ChatMessage)
            .join(ChatSession, ChatSession.id == ChatMessage.session_id)
            .where(
                ChatMessage.id == message_id,
                ChatMessage.company_code == company_code,
                ChatSession.company_code == company_code,
                ChatSession.patient_id == patient_id,
            )
        )
        res = await db.execute(stmt_find)
        m = res.scalar_one_or_none()
        if not m:
            return False

        if not hasattr(m, "is_deleted"):
            return False

        m.is_deleted = True  # type: ignore[attr-defined]
        await db.flush()
        return True

    # =========================
    # Citations (optional)
    # =========================
    @staticmethod
    async def get_citations_for_assistant_message(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        assistant_message_id: UUID,
    ) -> list[dict[str, Any]]:
        stmt_check = (
            select(ChatMessage.id)
            .join(ChatSession, ChatSession.id == ChatMessage.session_id)
            .where(
                ChatMessage.id == assistant_message_id,
                ChatMessage.company_code == company_code,
                ChatSession.company_code == company_code,
                ChatSession.patient_id == patient_id,
            )
        )
        res = await db.execute(stmt_check)
        ok = res.scalar_one_or_none()
        if not ok:
            return []

        chk = await db.execute(text("SELECT to_regclass('public.vw_chat_message_citations')"))
        view_name = chk.scalar_one_or_none()
        if not view_name:
            return []

        stmt = text(
            """
            SELECT *
            FROM public.vw_chat_message_citations
            WHERE company_code = :cc
              AND assistant_message_id = :mid
            ORDER BY score DESC NULLS LAST
            """
        )
        res2 = await db.execute(stmt, {"cc": company_code, "mid": str(assistant_message_id)})
        return [dict(r) for r in res2.mappings().all()]
