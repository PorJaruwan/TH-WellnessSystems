# app/api/v1/modules/ai/services/ai_consult_service.py

from __future__ import annotations

import uuid
from typing import Any, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ai_topics import AITopic
from app.api.v1.modules.ai.models.chat_models import ChatSession  # ✅ ใช้ตัวนี้ (ตรงกับไฟล์ chat_models.py)

from app.api.v1.modules.ai.schemas.ai_consult_model import (
    AITopicItem,
    AITopicCards,
)

DEFAULT_DISCLAIMER_TH = (
    "ข้อมูลทั่วไปเพื่อการให้ความรู้ ไม่ใช่คำแนะนำทางการแพทย์ "
    "หากมีอาการรุนแรง/ฉุกเฉินให้ติดต่อโรงพยาบาลทันที"
)
DEFAULT_DISCLAIMER_EN = (
    "General information only, not medical advice. "
    "If severe/emergency symptoms occur, seek urgent medical care."
)


def _to_uuid(v: str | uuid.UUID) -> uuid.UUID:
    if isinstance(v, uuid.UUID):
        return v
    return uuid.UUID(str(v))


def _norm_lang(lang: str | None) -> str:
    if not lang:
        return "TH"
    u = lang.upper()
    if u.startswith("EN") or "EN" in u:
        return "EN"
    return "TH"


def _pick_label(t: AITopic, lang: str) -> str:
    return t.label_en if (lang == "EN" and t.label_en) else t.label_th


def _pick_desc(t: AITopic, lang: str) -> str | None:
    if lang == "EN":
        return t.description_en or t.description_th
    return t.description_th or t.description_en


def _parse_default_cards(default_cards: object) -> AITopicCards:
    """
    รองรับ 2 format:
      A) {causes:[...], self_care:[...], red_flags:[...]}
      B) [{type:"causes", items:[...]}, ...]
    """
    cards = AITopicCards()

    if isinstance(default_cards, dict):
        cards.causes = [str(x) for x in (default_cards.get("causes") or [])]
        cards.self_care = [str(x) for x in (default_cards.get("self_care") or [])]
        cards.red_flags = [str(x) for x in (default_cards.get("red_flags") or [])]
        return cards

    if isinstance(default_cards, list):
        for block in default_cards:
            if not isinstance(block, dict):
                continue
            t = (block.get("type") or "").lower()
            items = block.get("items") or []
            if not isinstance(items, list):
                continue

            if t in ("cause", "causes"):
                cards.causes = [str(x) for x in items]
            elif t in ("self_care", "selfcare", "care"):
                cards.self_care = [str(x) for x in items]
            elif t in ("red_flags", "redflag", "redflags", "when_to_see_doctor"):
                cards.red_flags = [str(x) for x in items]

    return cards


async def list_ai_topics(
    db: AsyncSession,
    *,
    company_code: str,
    lang: str | None = None,
) -> list[AITopicItem]:
    lang2 = _norm_lang(lang)

    q = (
        select(AITopic)
        .where(AITopic.company_code == company_code, AITopic.is_active.is_(True))
        .order_by(AITopic.sort_order.asc(), AITopic.topic_code.asc())
    )
    res = await db.execute(q)
    rows = res.scalars().all()

    return [
        AITopicItem(
            topic_code=r.topic_code,
            label=_pick_label(r, lang2),
            description=_pick_desc(r, lang2),
            sort_order=r.sort_order,
        )
        for r in rows
    ]


async def get_ai_topic_cards(
    db: AsyncSession,
    *,
    company_code: str,
    topic_code: str,
    lang: str | None = None,
):
    lang2 = _norm_lang(lang)

    q = select(AITopic).where(
        AITopic.company_code == company_code,
        AITopic.topic_code == topic_code,
        AITopic.is_active.is_(True),
    )
    res = await db.execute(q)
    topic = res.scalar_one_or_none()
    if not topic:
        return None

    cards = _parse_default_cards(topic.default_cards)
    disclaimer = DEFAULT_DISCLAIMER_EN if lang2 == "EN" else DEFAULT_DISCLAIMER_TH

    return topic, cards, disclaimer


# ============================================================
# AI Consult Sessions (Create or Re-use active session) - ORM
# ============================================================

async def create_or_get_ai_consult_session(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    topic_code: str,
    language: str,
    entry_point: str,
) -> Tuple[dict[str, Any] | None, str]:
    """
    กันสร้าง session ซ้ำ:
      - ถ้ามี ACTIVE session เดิมของ patient+topic เดียวกัน (ai_consult/patient)
        -> return session เดิม (flag="REUSED")
      - ไม่งั้นสร้างใหม่ (flag="CREATED")
    """

    # 1) Validate topic exists & active
    chk = await db.execute(
        select(AITopic.id).where(
            AITopic.company_code == company_code,
            AITopic.topic_code == topic_code,
            AITopic.is_active.is_(True),
        )
    )
    if chk.scalar_one_or_none() is None:
        return None, "TOPIC_NOT_FOUND"

    pid = _to_uuid(patient_id)

    # 2) Find active session (ORM)
    q_find = (
        select(ChatSession)
        .where(
            ChatSession.company_code == company_code,
            ChatSession.patient_id == pid,
            ChatSession.app_context == "ai_consult",
            ChatSession.channel == "patient",
            ChatSession.status == "active",
            ChatSession.topic_code == topic_code,
        )
        .order_by(func.coalesce(ChatSession.last_activity_at, ChatSession.created_at).desc())
        .limit(1)
    )

    res = await db.execute(q_find)
    sess = res.scalar_one_or_none()

    if sess:
        out = {
            "session_id": str(sess.id),
            "company_code": sess.company_code,
            "patient_id": str(sess.patient_id),
            "topic_code": sess.topic_code,
            "language": sess.language or "th-TH",
            "entry_point": (sess.meta or {}).get("entry_point", "pre_consult"),  # ✅ meta ไม่ใช่ metadata
            "app_context": sess.app_context or "ai_consult",
            "channel": sess.channel or "patient",
            "status": sess.status or "active",
        }
        return out, "REUSED"

    # 3) Create new session (ORM object)
    new_session = ChatSession(
        company_code=company_code,
        patient_id=pid,
        app_context="ai_consult",
        channel="patient",
        status="active",  # override default "open"
        topic_code=topic_code,
        language=language or "th-TH",
        last_activity_at=func.now(),
        meta={"entry_point": entry_point or "pre_consult"},  # ✅ meta ไม่ใช่ metadata
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    out = {
        "session_id": str(new_session.id),
        "company_code": new_session.company_code,
        "patient_id": str(new_session.patient_id),
        "topic_code": new_session.topic_code,
        "language": new_session.language or "th-TH",
        "entry_point": (new_session.meta or {}).get("entry_point", "pre_consult"),
        "app_context": new_session.app_context or "ai_consult",
        "channel": new_session.channel or "patient",
        "status": new_session.status or "active",
    }
    return out, "CREATED"

