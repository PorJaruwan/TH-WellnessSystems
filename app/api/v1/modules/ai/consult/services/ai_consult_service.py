# app/api/v1/modules/ai/consult/services/ai_consult_service.py

from __future__ import annotations

import uuid
from typing import Any, Tuple

from sqlalchemy import select, func, text, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB

import logging

logger = logging.getLogger(__name__)


from app.db.models.ai_topics import AITopic
from app.api.v1.modules.chat.models.chat_models import ChatSession  # ✅ ใช้ตัวนี้ (ตรงกับไฟล์ chat_models.py)

from app.api.v1.modules.ai.consult.schemas.ai_consult_model import (
    AITopicItem,
    AITopicCards,
)

from app.api.v1.modules.chat.models.chat_models import ChatMessage

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


# ============================================================
# Quick Actions (Chips): Causes / Self-care / When to see doctor
# ============================================================

def _action_title(action: str, lang: str) -> str:
    if lang == "EN":
        return {
            "causes": "Possible causes",
            "self_care": "Self-care",
            "red_flags": "When to see a doctor",
        }.get(action, "Quick info")
    return {
        "causes": "อาจเกิดจาก",
        "self_care": "ดูแลเบื้องต้น",
        "red_flags": "ควรพบแพทย์เมื่อ",
    }.get(action, "ข้อมูลเพิ่มเติม")


def _bullets(items: list[str]) -> str:
    if not items:
        return ""
    return "\n".join([f"• {x}" for x in items])


def _default_chips(lang: str) -> list[dict[str, Any]]:
    if lang == "EN":
        return [
            {"type": "chip", "label": "Causes", "action": {"type": "quick", "value": "causes"}},
            {"type": "chip", "label": "Self-care", "action": {"type": "quick", "value": "self_care"}},
            {"type": "chip", "label": "When to see a doctor", "action": {"type": "quick", "value": "red_flags"}},
        ]
    return [
        {"type": "chip", "label": "Causes", "action": {"type": "quick", "value": "causes"}},
        {"type": "chip", "label": "Self-care", "action": {"type": "quick", "value": "self_care"}},
        {"type": "chip", "label": "When to see a doctor", "action": {"type": "quick", "value": "red_flags"}},
    ]


async def run_quick_action(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: str | uuid.UUID,
    action: str,
    lang: str | None = None,
) -> dict[str, Any] | str:
    """Execute a quick action and append an assistant message into chat_messages.

    Returns:
      - "SESSION_NOT_FOUND" | "TOPIC_NOT_SET" | "TOPIC_NOT_FOUND"
      - dict payload (assistant_text, triage, ui_cards, retrieval)
    """

    sid = _to_uuid(session_id)
    pid = _to_uuid(patient_id)

    # 1) owned session
    q_sess = select(ChatSession).where(
        ChatSession.id == sid,
        ChatSession.company_code == company_code,
        ChatSession.patient_id == pid,
    )    
    sess = (await db.execute(q_sess)).scalar_one_or_none()
    if not sess:
        return "SESSION_NOT_FOUND"

    # ✅ cache primitives (กัน greenlet_spawn)
    topic_code = sess.topic_code
    if not topic_code:
        return "TOPIC_NOT_SET"

    lang2 = _norm_lang(lang or sess.language)


    # 2) topic cards
    res = await get_ai_topic_cards(db, company_code=company_code, topic_code=topic_code, lang=lang2)
    if not res:
        return "TOPIC_NOT_FOUND"
    _topic, cards, disclaimer = res

    items: list[str]
    if action == "causes":
        items = cards.causes
    elif action == "self_care":
        items = cards.self_care
    else:
        items = cards.red_flags

    title = _action_title(action, lang2)
    body = _bullets(items)

    if lang2 == "EN":
        empty_msg = "No predefined items for this topic yet. Please describe your symptoms and I’ll help assess." 
    else:
        empty_msg = "ยังไม่มีรายการสำเร็จรูปสำหรับหัวข้อนี้ กรุณาเล่าอาการเพิ่มเติม แล้วฉันจะช่วยประเมินเบื้องต้น" 

    assistant_text = f"{title}\n{body}".strip() if body else f"{title}\n{empty_msg}"
    assistant_text = f"{assistant_text}\n\n{disclaimer}".strip()

    triage: dict[str, Any] = {}
    ui_cards: list[dict[str, Any]] = _default_chips(lang2)

    # If user asks "When to see a doctor", surface escalation CTA.
    if action == "red_flags" and items:
        if lang2 == "EN":
            triage = {"level": "recommended", "reason": "Some symptoms may require medical evaluation."}
        else:
            triage = {"level": "recommended", "reason": "มีอาการบางอย่างที่ควรพบแพทย์เพื่อประเมินเพิ่มเติม"}

        ui_cards.append(
            {"type": "cta", "label": "Doctor Consultation Recommended", "action": {"type": "open_escalation"}}
        )

        # Stamp triage into session header for UI
        sess.triage_level = triage.get("level")
        sess.triage_reason = triage.get("reason")

    # 3) append assistant message
    asst_msg = ChatMessage(
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
    db.add(asst_msg)
    await db.commit()

    return {
        "assistant_text": assistant_text,
        "triage": triage,
        "ui_cards": ui_cards,
        "retrieval": None,
    }



# ============================================================
# Escalation (Handoff to Booking)
# ============================================================


def _safe_str(v) -> str | None:
    if v is None:
        return None
    return str(v)


async def create_escalation_handoff(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: str | uuid.UUID,
    triage_level: str | None = None,
    reason: str | None = None,
    urgency: str | None = None,
    note: str | None = None,
    lang: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | str:
    """Create chat_escalations row and return a booking handoff payload.

    Preferred implementation: call DB RPC `public.rpc_request_escalation(...)` (from V5_full).
    Fallback: insert into chat_escalations directly and stamp chat_sessions metadata.

    Returns:
      - "SESSION_NOT_FOUND"
      - dict payload (escalation_id, deeplink, handoff)
    """

    sid = _to_uuid(session_id)
    pid = _to_uuid(patient_id)

    # 1) owned session
    q_sess = select(ChatSession).where(
        ChatSession.id == sid,
        ChatSession.company_code == company_code,
        ChatSession.patient_id == pid,
    )
    sess = (await db.execute(q_sess)).scalar_one_or_none()
    if not sess:
        return "SESSION_NOT_FOUND"

    # ------------------------------------------------------------
    # IMPORTANT (Async SQLAlchemy):
    # Do NOT access ORM attributes after commit/rollback.
    # Rollback can expire ORM objects and trigger lazy IO which
    # causes: greenlet_spawn has not been called (await_only()).
    # Cache everything we need NOW (primitives only).
    # ------------------------------------------------------------
    sess_patient_id = _safe_str(sess.patient_id)
    sess_language = sess.language
    sess_topic_code = sess.topic_code  # ✅ correct
    sess_triage_reason = sess.triage_reason
    sess_triage_level = sess.triage_level

    # 2) derive defaults
    lang2 = _norm_lang(lang or sess_language)  # cached
    topic_code = sess_topic_code  # cached

    # Normalize reason: prefer request reason, then session triage_reason
    final_reason = (reason or sess_triage_reason or "").strip() or None
    final_triage = (triage_level or sess_triage_level or "").strip() or None

    # Escalation metadata (keep small + UI friendly)
    meta: dict[str, Any] = {}
    if isinstance(metadata, dict):
        meta.update(metadata)
    if topic_code:
        meta.setdefault("topic_code", topic_code)
    if urgency:
        meta.setdefault("urgency", urgency)
    if note:
        meta.setdefault("note", note)
    meta.setdefault("source", "ai_consult")

    escalation_id: str | None = None

    # 3) Try RPC first (recommended; matches DB design you provided)
    try:
        rpc_sql = text(
            "select public.rpc_request_escalation(:sid, :triage_level, :reason, :metadata) as escalation_id"
        ).bindparams(
            bindparam("metadata", type_=JSONB)
        )

        res = await db.execute(
            rpc_sql,
            {
                "sid": sid,
                "triage_level": final_triage,
                "reason": final_reason,
                "metadata": meta,
            },
        )

        escalation_id = _safe_str(res.scalar_one_or_none())

        if not escalation_id:
            raise RuntimeError("rpc_request_escalation returned null")

        await db.commit()

    except Exception as e:
        # 🔴 สำคัญมาก: ต้อง rollback ก่อน
        await db.rollback()

        logger.exception("rpc_request_escalation failed, fallback to direct insert")

        insert_sql = text("""
            insert into public.chat_escalations
            (session_id, company_code, triage_level, reason, metadata)
            values (:sid, :company_code, :triage_level, :reason, :metadata)
            returning id
        """).bindparams(
            bindparam("metadata", type_=JSONB)
        )

        res2 = await db.execute(
            insert_sql,
            {
                "sid": sid,
                "company_code": company_code,
                "triage_level": final_triage,
                "reason": final_reason,
                "metadata": meta,
            },
        )

        escalation_id = _safe_str(res2.scalar_one_or_none())

        await db.commit()


    if not escalation_id:
        # rare, but keep safe
        raise RuntimeError("failed to create escalation")

    # 5) Build handoff payload for booking page prefill
    # Note: keep it consistent with your DB/RPC design.
    handoff = {
        "handoff_type": "booking_prefill",
        "escalation_id": escalation_id,
        "session_id": str(sid),
        "company_code": company_code,
        "patient_id": sess_patient_id,  # cached (avoid ORM IO after commit/rollback)
        "topic_code": topic_code,
        "triage": {"level": final_triage, "reason": final_reason},
        "prefill": {
            "reason": final_reason,
            "topic_code": topic_code,
            "triage_level": final_triage,
            "triage_reason": final_reason,
            "urgency": urgency,
            "note": note,
        },
    }

    # Optional deeplink convention (your FlutterFlow can map this)
    deeplink = f"wellplus://booking?handoff_id={escalation_id}&session_id={sid}"

    return {
        "escalation_id": escalation_id,
        "session_id": str(sid),
        "company_code": company_code,
        "patient_id": sess_patient_id,  # cached (avoid ORM IO after commit/rollback)
        "topic_code": topic_code,
        "triage_level": final_triage,
        "reason": final_reason,
        "urgency": urgency,
        "deeplink": deeplink,
        "handoff": handoff,
    }

async def list_my_ai_sessions(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    status: str = "active",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List AI consult sessions for resume.

    Filter:
      - app_context='ai_consult'
      - channel='patient'
      - patient_id ของคนปัจจุบัน
      - status: active|closed|all (อื่น ๆ -> active)
    """

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

    q = (
        select(ChatSession)
        .where(*conds)
        .order_by(func.coalesce(ChatSession.last_activity_at, ChatSession.created_at).desc())
        .limit(limit)
    )
    res = await db.execute(q)
    rows = res.scalars().all()

    items: list[dict[str, Any]] = []
    for s in rows:
        meta = getattr(s, "meta", None) or getattr(s, "metadata", None) or {}
        items.append(
            {
                "session_id": str(s.id),
                "company_code": s.company_code,
                "patient_id": str(s.patient_id) if s.patient_id else None,
                "topic_code": s.topic_code,
                "language": s.language,
                "status": s.status,
                "last_activity_at": s.last_activity_at.isoformat() if s.last_activity_at else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "entry_point": meta.get("entry_point") if isinstance(meta, dict) else None,
            }
        )
    return items
