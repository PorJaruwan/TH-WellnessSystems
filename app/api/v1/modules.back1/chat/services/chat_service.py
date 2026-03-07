# app/api/v1/modules/chat/services/chat_service.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.chat.repositories.chat_repository import ChatRepository


class ChatService:
    """Use-case / business logic layer for Chat."""

    # -------- Sessions --------
    @staticmethod
    async def get_session_header(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
    ) -> Optional[dict[str, Any]]:
        try:
            dto = await ChatRepository.get_session_header(
                db,
                company_code=company_code,
                patient_id=patient_id,
                session_id=session_id,
            )
            return dto.__dict__ if dto else None
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def list_my_sessions(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        status: str = "open",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        try:
            return await ChatRepository.list_my_sessions_summary(
                db,
                company_code=company_code,
                patient_id=patient_id,
                status=status,
                limit=limit,
                offset=offset,
            )
        except Exception:
            await db.rollback()
            raise


    @staticmethod
    async def create_session(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        topic_code: Optional[str] = None,
        language: str = "th-TH",
        channel: str = "flutterflow",
        reuse_open: bool = True,
    ) -> dict[str, Any]:
        """Create a new session.

        If reuse_open=True and DB enforces unique open session per patient, this will return
        the existing open session when unique violation happens.
        """
        try:
            if not reuse_open:
                s = await ChatRepository.create_patient_session(
                    db,
                    company_code=company_code,
                    patient_id=patient_id,
                    topic_code=topic_code,
                    language=language,
                    channel=channel,
                )
                await db.commit()
                return {
                    "session_id": s.id,
                    "status": s.status,
                    "topic_code": s.topic_code,
                    "language": s.language,
                    "last_activity_at": s.last_activity_at,
                    "created_at": s.created_at,
                }

            try:
                s = await ChatRepository.create_patient_session(
                    db,
                    company_code=company_code,
                    patient_id=patient_id,
                    topic_code=topic_code,
                    language=language,
                    channel=channel,
                )
                await db.commit()
                return {
                    "session_id": s.id,
                    "status": s.status,
                    "topic_code": s.topic_code,
                    "language": s.language,
                    "last_activity_at": s.last_activity_at,
                    "created_at": s.created_at,
                }
            except IntegrityError:
                await db.rollback()
                rows = await ChatRepository.list_my_sessions_summary(
                    db,
                    company_code=company_code,
                    patient_id=patient_id,
                    status="open",
                    limit=1,
                )
                if rows:
                    return rows[0]
                raise

        except Exception:
            # ✅ safety net for any unexpected errors
            await db.rollback()
            raise

    @staticmethod
    async def close_session(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
    ) -> Optional[dict[str, Any]]:
        try:
            dto = await ChatRepository.close_session(
                db,
                company_code=company_code,
                patient_id=patient_id,
                session_id=session_id,
            )
            if not dto:
                return None
            await db.commit()
            return dto.__dict__
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def reopen_session(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
    ) -> Optional[dict[str, Any]]:
        try:
            dto = await ChatRepository.reopen_session(
                db,
                company_code=company_code,
                patient_id=patient_id,
                session_id=session_id,
            )
            if not dto:
                return None
            await db.commit()
            return dto.__dict__
        except Exception:
            await db.rollback()
            raise

    # -------- Messages --------
    @staticmethod
    async def list_messages(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
        limit: int = 50,
        before: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        try:
            owned = await ChatRepository.get_owned_session(
                db,
                company_code=company_code,
                patient_id=patient_id,
                session_id=session_id,
            )
            if not owned:
                return []

            rows = await ChatRepository.list_messages(
                db,
                company_code=company_code,
                session_id=session_id,
                limit=limit,
                before=before,
            )
            rows = list(reversed(rows))
            return [
                {
                    "id": m.id,
                    "session_id": m.session_id,
                    "role": m.role,
                    "content": m.content,
                    "content_json": m.content_json or {},
                    "created_at": m.created_at,
                }
                for m in rows
            ]
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def send_message(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        session_id: UUID,
        text: str,
    ) -> dict[str, Any] | str:
        try:
            owned = await ChatRepository.get_owned_session(
                db,
                company_code=company_code,
                patient_id=patient_id,
                session_id=session_id,
            )
            if not owned:
                return "SESSION_NOT_FOUND"

            # 1) insert user message
            await ChatRepository.insert_message(
                db,
                company_code=company_code,
                session_id=session_id,
                role="user",
                content=text,
                content_json={},
            )

            # 2) TODO: replace stub with real RAG/LLM
            triage: dict[str, Any] = {}
            ui_cards: list[dict[str, Any]] = []
            lowered = text.lower()
            if any(k in lowered for k in ["แน่นหน้าอก", "หายใจไม่ออก", "ชัก", "หมดสติ"]):
                triage = {"level": "urgent", "reason": "มีอาการที่ควรพบแพทย์โดยเร็ว"}
                ui_cards.append(
                    {
                        "type": "cta",
                        "label": "Doctor Consultation Recommended",
                        "action": {"type": "open_escalation"},
                    }
                )

            assistant_text = "รับทราบครับ/ค่ะ เล่าอาการเพิ่มเติมได้เลย (ระยะเวลา, ความรุนแรง, อาการร่วม) เพื่อช่วยประเมินเบื้องต้น"

            await ChatRepository.insert_message(
                db,
                company_code=company_code,
                session_id=session_id,
                role="assistant",
                content=assistant_text,
                content_json={"triage": triage, "ui_cards": ui_cards, "retrieval": None},
            )

            if triage.get("level"):
                owned.triage_level = triage.get("level")
                owned.triage_reason = triage.get("reason")

            await db.commit()
            return {
                "assistant_text": assistant_text,
                "triage": triage,
                "ui_cards": ui_cards,
                "retrieval": None,
            }
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def soft_delete_message(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        message_id: UUID,
    ) -> bool:
        try:
            ok = await ChatRepository.soft_delete_message(
                db,
                company_code=company_code,
                patient_id=patient_id,
                message_id=message_id,
            )
            if not ok:
                return False
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            raise

    # -------- Citations --------
    @staticmethod
    async def get_citations(
        db: AsyncSession,
        *,
        company_code: str,
        patient_id: UUID,
        assistant_message_id: UUID,
    ) -> list[dict[str, Any]]:
        try:
            return await ChatRepository.get_citations_for_assistant_message(
                db,
                company_code=company_code,
                patient_id=patient_id,
                assistant_message_id=assistant_message_id,
            )
        except Exception:
            await db.rollback()
            raise


# ---------- Backward compatible function exports (router imports stay stable) ----------

async def get_chat_session_header(db: AsyncSession, *, company_code: str, patient_id: str, session_id: UUID):
    return await ChatService.get_session_header(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
        session_id=session_id,
    )


async def list_chat_messages(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: UUID,
    limit: int = 50,
    offset: int = 0,
    before: Optional[datetime] = None,
) -> tuple[list[dict[str, Any]], int]:
    """Backward compatible wrapper for routers.

    Returns (items, total) where items are dict-like rows.
    """
    # ensure ownership
    owned = await ChatRepository.get_owned_session(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
        session_id=session_id,
    )
    if not owned:
        return [], 0

    rows, total = await ChatRepository.list_messages(
        db,
        company_code=company_code,
        session_id=session_id,
        limit=limit,
        offset=offset,
        before=before,
    )

    # rows returned newest->oldest; reverse to chronological
    rows = list(reversed(rows))
    items = [
        {
            "id": m.id,
            "session_id": m.session_id,
            "role": m.role,
            "content": m.content,
            "content_json": m.content_json or {},
            "created_at": m.created_at,
        }
        for m in rows
    ]
    return items, int(total)


async def send_chat_message(db: AsyncSession, *, company_code: str, patient_id: str, session_id: UUID, text: str):
    return await ChatService.send_message(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
        session_id=session_id,
        text=text,
    )


async def close_chat_session(db: AsyncSession, *, company_code: str, patient_id: str, session_id: UUID):
    return await ChatService.close_session(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
        session_id=session_id,
    )
