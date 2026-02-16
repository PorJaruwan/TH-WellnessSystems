# app/api/v1/modules/chat/services/chat_service.py

from __future__ import annotations
from datetime import datetime, timezone
import uuid
from typing import Optional, Any
from uuid import UUID

from sqlalchemy import select, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.chat.models.chat_models import ChatSession, ChatMessage


def _now():
    return datetime.now(timezone.utc)


async def _get_owned_session(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: UUID,
) -> Optional[ChatSession]:
    q = (
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .where(ChatSession.company_code == company_code)
        .where(ChatSession.patient_id == UUID(patient_id))
    )
    return (await db.execute(q)).scalar_one_or_none()


async def get_chat_session_header(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: UUID,
):
    s = await _get_owned_session(db, company_code=company_code, patient_id=patient_id, session_id=session_id)
    if not s:
        return None

    return {
        "session_id": s.id,
        "topic": s.topic_code,
        "triage_level": s.triage_level,
        "triage_reason": s.triage_reason,
        "last_activity_at": s.last_activity_at,
        "status": s.status,
    }


async def list_chat_messages(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: UUID,
    limit: int = 50,
    before: Optional[datetime] = None,
):
    s = await _get_owned_session(db, company_code=company_code, patient_id=patient_id, session_id=session_id)
    if not s:
        return []

    q = (
        select(ChatMessage)
        .where(ChatMessage.company_code == company_code)
        .where(ChatMessage.session_id == session_id)
        .where(ChatMessage.is_deleted == False)  # noqa: E712
    )

    if before:
        q = q.where(ChatMessage.created_at < before)

    # timeline: ดึงล่าสุดก่อน แล้วค่อย reverse ให้ UI
    q = q.order_by(desc(ChatMessage.created_at)).limit(limit)
    rows = (await db.execute(q)).scalars().all()
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


async def send_chat_message(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: UUID,
    text: str,
):
    s = await _get_owned_session(db, company_code=company_code, patient_id=patient_id, session_id=session_id)
    if not s:
        return "SESSION_NOT_FOUND"

    # 1) insert user message
    user_msg = ChatMessage(
        company_code=company_code,
        session_id=session_id,
        role="user",
        content=text,
        content_json={},
    )
    db.add(user_msg)

    # 2) TODO: call AI จริง / RAG จริง (ตอนนี้ stub)
    triage = {}
    ui_cards = []
    lowered = text.lower()
    if any(k in lowered for k in ["แน่นหน้าอก", "หายใจไม่ออก", "ชัก", "หมดสติ"]):
        triage = {"level": "urgent", "reason": "มีอาการที่ควรพบแพทย์โดยเร็ว"}
        ui_cards.append({"type": "cta", "label": "Doctor Consultation Recommended", "action": {"type": "open_escalation"}})

    assistant_text = "รับทราบครับ/ค่ะ เล่าอาการเพิ่มเติมได้เลย (ระยะเวลา, ความรุนแรง, อาการร่วม) เพื่อช่วยประเมินเบื้องต้น"

    asst_msg = ChatMessage(
        company_code=company_code,
        session_id=session_id,
        role="assistant",
        content=assistant_text,
        content_json={
            "triage": triage,
            "ui_cards": ui_cards,
            "retrieval": None,
        },
    )
    db.add(asst_msg)

    # 3) last_activity_at: DB trigger ทำให้แล้วหลัง insert message:contentReference[oaicite:9]{index=9}
    # แต่ทำซ้ำแบบ safe ก็ได้ (ไม่จำเป็นต้องทำ ถ้าคุณอยากพึ่ง trigger 100%)
    # s.last_activity_at = _now()

    # 4) หากคุณต้องการ stamp triage ลง session ด้วย (เพื่อ header UI)
    if triage.get("level"):
        s.triage_level = triage.get("level")
        s.triage_reason = triage.get("reason")

    await db.commit()

    return {
        "assistant_text": assistant_text,
        "triage": triage,
        "ui_cards": ui_cards,
        "retrieval": None,
    }

async def close_chat_session(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: UUID,
) -> dict[str, Any] | None:
    """Close a chat session (set status='closed').

    - Validates session ownership (company_code + patient_id)
    - Idempotent: calling close again keeps status='closed'
    """
    pid = uuid.UUID(str(patient_id))

    chk = await db.execute(
        select(ChatSession.id).where(
            ChatSession.company_code == company_code,
            ChatSession.id == session_id,
            ChatSession.patient_id == pid,
        )
    )
    if chk.scalar_one_or_none() is None:
        return None

    await db.execute(
        text(
            """
            update public.chat_sessions
               set status = 'closed',
                   updated_at = now(),
                   last_activity_at = now(),
                   metadata = coalesce(metadata, '{}'::jsonb) || (:patch)::jsonb
             where id = :sid
               and company_code = :cc
               and patient_id = :pid
            """
        ),
        {
            "sid": str(session_id),
            "cc": company_code,
            "pid": str(pid),
            "patch": '{"closed_by":"patient"}',
        },
    )
    await db.commit()

   # ✅ return header ตัวเต็ม (เหมือน GET /sessions/{session_id})
    return await get_chat_session_header(
        db,
        company_code=company_code,
        patient_id=str(pid),
        session_id=session_id,
        #"status": "closed",
    )

