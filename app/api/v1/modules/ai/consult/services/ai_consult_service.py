# # app/api/v1/modules/ai/consult/services/ai_consult_service.py
from __future__ import annotations

import uuid
from typing import Any, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, text, bindparam
from sqlalchemy.dialects.postgresql import JSONB

from app.db.models.ai_topics import AITopic
from app.api.v1.modules.chat.models.chat_models import ChatSession, ChatMessage
from app.api.v1.modules.ai.consult.models.dtos import (
    AITopicItem,
    AITopicsList,
    AITopicCards,
    AITopicCardsPayload,
)
from app.api.v1.modules.ai.consult.repositories.ai_topics_repository import (
    AITopicsRepository,
)

DEFAULT_DISCLAIMER_TH = (
    "ข้อมูลทั่วไปเพื่อการให้ความรู้ ไม่ใช่คำแนะนำทางการแพทย์ "
    "หากมีอาการรุนแรง/ฉุกเฉินให้ติดต่อโรงพยาบาลทันที"
)
DEFAULT_DISCLAIMER_EN = (
    "General information only, not medical advice. "
    "If severe/emergency symptoms occur, seek urgent medical care."
)


class AITopicsService:
    def __init__(self, repo: AITopicsRepository):
        self.repo = repo

    @staticmethod
    def _to_iso(v):
        return v.isoformat() if v else None

    @staticmethod
    def _norm_lang(lang: str | None) -> str:
        if not lang:
            return "TH"
        value = lang.strip().upper()
        if value.startswith("EN") or "EN" in value:
            return "EN"
        return "TH"

    def _pick_label_from_row(self, row: dict[str, Any], lang: str) -> str:
        if lang == "EN":
            return (
                row.get("topic_name_en")
                or row.get("label_en")
                or row.get("topic_name_th")
                or row.get("label_th")
                or row.get("topic_code")
            )
        return (
            row.get("topic_name_th")
            or row.get("label_th")
            or row.get("topic_name_en")
            or row.get("label_en")
            or row.get("topic_code")
        )

    def _pick_desc_from_row(self, row: dict[str, Any], lang: str) -> str | None:
        if lang == "EN":
            return row.get("description_en") or row.get("description_th")
        return row.get("description_th") or row.get("description_en")

    def _pick_category_name_from_row(self, row: dict[str, Any], lang: str) -> str | None:
        if lang == "EN":
            return row.get("category_name_en") or row.get("category_name_th")
        return row.get("category_name_th") or row.get("category_name_en")

    def _map_item(self, row: dict[str, Any], lang: str) -> AITopicItem:
        return AITopicItem(
            id=str(row["id"]) if row.get("id") else None,
            company_code=row.get("company_code"),
            topic_code=row["topic_code"],
            label=self._pick_label_from_row(row, lang),
            description=self._pick_desc_from_row(row, lang),
            sort_order=row.get("sort_order", 0),
            category_id=str(row["ai_topic_category_id"]) if row.get("ai_topic_category_id") else None,
            category_code=row.get("category_code"),
            category_name=self._pick_category_name_from_row(row, lang),
            parent_category_id=str(row["parent_category_id"]) if row.get("parent_category_id") else None,
            topic_type=row.get("topic_type"),
            topic_level=row.get("topic_level"),
            intent_code=row.get("intent_code"),
            output_format=row.get("output_format"),
            action_type=row.get("action_type"),
            requires_auth=bool(row.get("requires_auth", False)),
            requires_patient_context=bool(row.get("requires_patient_context", False)),
            requires_booking_context=bool(row.get("requires_booking_context", False)),
            requires_payment_context=bool(row.get("requires_payment_context", False)),
            requires_service_context=bool(row.get("requires_service_context", False)),
            is_active=bool(row.get("is_active", True)),
            is_system=bool(row.get("is_system", True)),
            is_default=bool(row.get("is_default", False)),
            version_no=int(row.get("version_no", 1) or 1),
            created_at=self._to_iso(row.get("created_at")),
            updated_at=self._to_iso(row.get("updated_at")),
        )

    @staticmethod
    def _parse_default_cards(default_cards: object) -> AITopicCards:
        cards = AITopicCards()

        if isinstance(default_cards, dict):
            cards.check = [str(x) for x in (default_cards.get("check") or [])]
            cards.self_care = [str(x) for x in (default_cards.get("self_care") or [])]
            cards.red_flag = [
                str(x)
                for x in (default_cards.get("red_flag") or default_cards.get("red_flags") or [])
            ]
            cards.cause = [str(x) for x in (default_cards.get("cause") or [])]
            return cards

        if isinstance(default_cards, list):
            for block in default_cards:
                if not isinstance(block, dict):
                    continue
                block_type = (block.get("type") or "").lower()
                items = block.get("items") or []
                if not isinstance(items, list):
                    continue

                if block_type in ("check", "assessment", "questions"):
                    cards.check = [str(x) for x in items]
                elif block_type in ("self_care", "selfcare", "care"):
                    cards.self_care = [str(x) for x in items]
                elif block_type in ("red_flag", "red_flags", "redflag", "redflags", "when_to_see_doctor"):
                    cards.red_flag = [str(x) for x in items]
                elif block_type in ("cause", "causes"):
                    cards.cause = [str(x) for x in items]
        return cards

    async def list_topics(
        self,
        *,
        company_code: Optional[str],
        lang: str | None,
        category_id: Optional[UUID],
        category_code: Optional[str],
        q: Optional[str],
        is_active: Optional[bool],
        include_uncategorized: bool,
        limit: int,
        offset: int,
        sort_by: str,
        sort_dir: str,
    ) -> tuple[AITopicsList, int]:
        lang_norm = self._norm_lang(lang)
        rows, total = await self.repo.list_topics(
            company_code=company_code,
            category_id=category_id,
            category_code=category_code,
            q=q,
            is_active=is_active,
            include_uncategorized=include_uncategorized,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        items = [self._map_item(row, lang_norm) for row in rows]
        return AITopicsList(items=items), total


    async def get_topic_cards(
        self,
        *,
        company_code: Optional[str],
        topic_code: str,
        lang: str | None,
    ) -> Optional[AITopicCardsPayload]:
        lang_norm = self._norm_lang(lang)
        row = await self.repo.get_topic_cards(
            company_code=company_code,
            topic_code=topic_code,
        )
        if not row:
            return None

        cards = self._parse_default_cards(row.get("default_cards"))
        disclaimer = DEFAULT_DISCLAIMER_EN if lang_norm == "EN" else DEFAULT_DISCLAIMER_TH

        return AITopicCardsPayload(
            topic_code=row["topic_code"],
            cards=cards,
            disclaimer=disclaimer,
        )


# =========================
# legacy helpers kept below
# =========================

def _to_uuid(v: str | uuid.UUID) -> uuid.UUID:
    if isinstance(v, uuid.UUID):
        return v
    return uuid.UUID(str(v))


async def create_or_get_ai_consult_session(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    topic_code: str,
    language: str,
    entry_point: str,
) -> Tuple[dict[str, Any] | None, str]:
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
            "entry_point": (sess.meta or {}).get("entry_point", "pre_consult"),
            "app_context": sess.app_context or "ai_consult",
            "channel": sess.channel or "patient",
            "status": sess.status or "active",
        }
        return out, "REUSED"

    new_session = ChatSession(
        company_code=company_code,
        patient_id=pid,
        app_context="ai_consult",
        channel="patient",
        status="active",
        topic_code=topic_code,
        language=language or "th-TH",
        last_activity_at=func.now(),
        meta={"entry_point": entry_point or "pre_consult"},
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


def _action_title(action: str, lang: str) -> str:
    if lang == "EN":
        return {
            "cause": "Possible cause",
            "self_care": "Self-care",
            "red_flag": "When to see a doctor",
        }.get(action, "Quick info")
    return {
        "cause": "อาจเกิดจาก",
        "self_care": "ดูแลเบื้องต้น",
        "red_flag": "ควรพบแพทย์เมื่อ",
    }.get(action, "ข้อมูลด่วน")



def _bullets(items: list[str]) -> str:
    if not items:
        return ""
    return "\n".join([f"• {x}" for x in items])


def _default_chips(lang: str) -> list[dict[str, Any]]:
    if lang == "EN":
        return [
            {"type": "chip", "label": "Causes", "action": {"type": "quick", "value": "cause"}},
            {"type": "chip", "label": "Self-care", "action": {"type": "quick", "value": "self_care"}},
            {"type": "chip", "label": "When to see a doctor", "action": {"type": "quick", "value": "red_flag"}},
        ]
    return [
        {"type": "chip", "label": "Causes", "action": {"type": "quick", "value": "cause"}},
        {"type": "chip", "label": "Self-care", "action": {"type": "quick", "value": "self_care"}},
        {"type": "chip", "label": "When to see a doctor", "action": {"type": "quick", "value": "red_flag"}},
    ]


# ============================================================
# backward-compatible wrappers for old routers
# ============================================================

async def list_ai_topics(
    db: AsyncSession,
    *,
    company_code: str,
    lang: str | None = None,
    category_id: UUID | None = None,
    q: str | None = None,
) -> list[AITopicItem]:
    """
    Legacy function kept for old routers.
    Returns only items list, matching old behavior.
    """
    repo = AITopicsRepository(db)
    service = AITopicsService(repo)

    payload, _total = await service.list_topics(
        company_code=company_code,
        lang=lang,
        category_id=category_id,
        q=q,
        is_active=True,
        include_uncategorized=True,
        limit=100,
        offset=0,
        sort_by="sort_order",
        sort_dir="asc",
    )
    return payload.items


async def get_ai_topic_cards(
    db: AsyncSession,
    *,
    company_code: str,
    topic_code: str,
    lang: str | None = None,
):
    """
    Legacy function kept for old routers/actions.
    Returns tuple(topic_like, cards, disclaimer) to preserve old contract.
    """
    repo = AITopicsRepository(db)
    service = AITopicsService(repo)

    row = await repo.get_topic_cards(
        company_code=company_code,
        topic_code=topic_code,
    )
    if not row:
        return None

    lang_norm = service._norm_lang(lang)
    cards = service._parse_default_cards(row.get("default_cards"))
    disclaimer = DEFAULT_DISCLAIMER_EN if lang_norm == "EN" else DEFAULT_DISCLAIMER_TH

    class _TopicLite:
        def __init__(self, topic_code: str):
            self.topic_code = topic_code

    topic = _TopicLite(topic_code=row["topic_code"])
    return topic, cards, disclaimer


async def run_quick_action(
    db: AsyncSession,
    *,
    company_code: str,
    patient_id: str,
    session_id: str | uuid.UUID,
    action: str,
    lang: str | None = None,
) -> dict[str, Any] | str:
    """
    Legacy quick action executor for old action router.
    """
    sid = _to_uuid(session_id)
    pid = _to_uuid(patient_id)

    q_sess = select(ChatSession).where(
        ChatSession.id == sid,
        ChatSession.company_code == company_code,
        ChatSession.patient_id == pid,
    )
    sess = (await db.execute(q_sess)).scalar_one_or_none()
    if not sess:
        return "SESSION_NOT_FOUND"

    topic_code = sess.topic_code
    if not topic_code:
        return "TOPIC_NOT_SET"

    lang2 = AITopicsService._norm_lang(lang or sess.language)

    res = await get_ai_topic_cards(
        db,
        company_code=company_code,
        topic_code=topic_code,
        lang=lang2,
    )
    if not res:
        return "TOPIC_NOT_FOUND"

    _topic, cards, disclaimer = res

    if action == "cause":
        items = cards.cause
    elif action == "self_care":
        items = cards.self_care
    elif action == "red_flag":
        items = cards.red_flag
    else:
        items = []

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

    if action == "red_flag" and items:
        if lang2 == "EN":
            triage = {"level": "recommended", "reason": "Some symptoms may require medical evaluation."}
        else:
            triage = {"level": "recommended", "reason": "มีอาการบางอย่างที่ควรพบแพทย์เพื่อประเมินเพิ่มเติม"}

        ui_cards.append(
            {"type": "cta", "label": "Doctor Consultation Recommended", "action": {"type": "open_escalation"}}
        )

        sess.triage_level = triage.get("level")
        sess.triage_reason = triage.get("reason")

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
    """
    Legacy escalation helper kept for routers that still import it.
    """
    sid = _to_uuid(session_id)
    pid = _to_uuid(patient_id)

    q_sess = select(ChatSession).where(
        ChatSession.id == sid,
        ChatSession.company_code == company_code,
        ChatSession.patient_id == pid,
    )
    sess = (await db.execute(q_sess)).scalar_one_or_none()
    if not sess:
        return "SESSION_NOT_FOUND"

    sess_patient_id = _safe_str(sess.patient_id)
    sess_language = sess.language
    sess_topic_code = sess.topic_code
    sess_triage_reason = getattr(sess, "triage_reason", None)
    sess_triage_level = getattr(sess, "triage_level", None)

    lang2 = AITopicsService._norm_lang(lang or sess_language)
    topic_code = sess_topic_code

    final_reason = (reason or sess_triage_reason or "").strip() or None
    final_triage = (triage_level or sess_triage_level or "").strip() or None

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

    try:
        rpc_sql = text(
            "select public.rpc_request_escalation(:sid, :triage_level, :reason, :metadata) as escalation_id"
        ).bindparams(bindparam("metadata", type_=JSONB))

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

    except Exception:
        await db.rollback()

        insert_sql = text(
            """
            insert into public.chat_escalations
            (session_id, company_code, triage_level, reason, metadata)
            values (:sid, :company_code, :triage_level, :reason, :metadata)
            returning id
            """
        ).bindparams(bindparam("metadata", type_=JSONB))

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
        raise RuntimeError("failed to create escalation")

    handoff = {
        "handoff_type": "booking_prefill",
        "escalation_id": escalation_id,
        "session_id": str(sid),
        "company_code": company_code,
        "patient_id": sess_patient_id,
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

    deeplink = f"wellplus://booking?handoff_id={escalation_id}&session_id={sid}"

    return {
        "escalation_id": escalation_id,
        "session_id": str(sid),
        "company_code": company_code,
        "patient_id": sess_patient_id,
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
    """
    Legacy helper kept for routers that still import it.
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
