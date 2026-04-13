from __future__ import annotations

from typing import Any
from uuid import UUID

from app.api.v1.modules.ai.consult.repositories.ai_consult_actions_repository import (
    AIConsultActionsRepository,
)
from app.api.v1.modules.ai.consult.services.ai_consult_service import (
    AITopicsService,
    get_ai_topic_cards,
    _action_title,
)


class AIConsultActionsService:
    """
    Enterprise service for AI consult session actions.
    Orchestrates business logic and delegates DB operations to repository.
    """

    def __init__(self, repo: AIConsultActionsRepository):
        self.repo = repo

    @staticmethod
    def _bullets(items: list[str]) -> str:
        if not items:
            return ""
        return "\n".join([f"• {x}" for x in items])

    @staticmethod
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

    async def _resolve_topic_cards(
        self,
        *,
        company_code: str,
        topic_code: str,
        lang: str,
    ):
        return await get_ai_topic_cards(
            self.repo.db,
            company_code=company_code,
            topic_code=topic_code,
            lang=lang,
        )

    def _select_items_by_action(self, *, action: str, cards) -> list[str]:
        if action == "cause":
            return cards.cause
        if action == "self_care":
            return cards.self_care
        if action == "red_flag":
            return cards.red_flag
        return []

    def _build_assistant_text(
        self,
        *,
        action: str,
        items: list[str],
        disclaimer: str,
        lang: str,
    ) -> str:
        title = _action_title(action, lang)
        body = self._bullets(items)

        if lang == "EN":
            empty_msg = "No predefined items for this topic yet. Please describe your symptoms and I’ll help assess."
        else:
            empty_msg = "ยังไม่มีรายการสำเร็จรูปสำหรับหัวข้อนี้ กรุณาเล่าอาการเพิ่มเติม แล้วฉันจะช่วยประเมินเบื้องต้น"

        assistant_text = f"{title}\n{body}".strip() if body else f"{title}\n{empty_msg}"
        return f"{assistant_text}\n\n{disclaimer}".strip()

    def _build_triage_and_cards(
        self,
        *,
        action: str,
        items: list[str],
        lang: str,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        triage: dict[str, Any] = {}
        ui_cards = self._default_chips(lang)

        if action == "red_flag" and items:
            if lang == "EN":
                triage = {
                    "level": "recommended",
                    "reason": "Some symptoms may require medical evaluation.",
                }
            else:
                triage = {
                    "level": "recommended",
                    "reason": "มีอาการบางอย่างที่ควรพบแพทย์เพื่อประเมินเพิ่มเติม",
                }

            ui_cards.append(
                {
                    "type": "cta",
                    "label": "Doctor Consultation Recommended",
                    "action": {"type": "open_escalation"},
                }
            )

        return triage, ui_cards

    async def run_quick_action(
        self,
        *,
        company_code: str,
        patient_id: str,
        session_id: UUID | str,
        action: str,
        lang: str | None = None,
    ) -> dict[str, Any] | str:
        sess = await self.repo.get_owned_session(
            company_code=company_code,
            patient_id=patient_id,
            session_id=session_id,
        )
        if not sess:
            return "SESSION_NOT_FOUND"

        topic_code = sess.topic_code
        if not topic_code:
            return "TOPIC_NOT_SET"

        lang_norm = AITopicsService._norm_lang(lang or sess.language)

        topic_result = await self._resolve_topic_cards(
            company_code=company_code,
            topic_code=topic_code,
            lang=lang_norm,
        )
        if not topic_result:
            return "TOPIC_NOT_FOUND"

        _topic, cards, disclaimer = topic_result
        items = self._select_items_by_action(action=action, cards=cards)

        assistant_text = self._build_assistant_text(
            action=action,
            items=items,
            disclaimer=disclaimer,
            lang=lang_norm,
        )

        triage, ui_cards = self._build_triage_and_cards(
            action=action,
            items=items,
            lang=lang_norm,
        )

        try:
            if triage:
                await self.repo.set_session_triage(session=sess, triage=triage)

            await self.repo.add_assistant_message(
                company_code=company_code,
                session_id=session_id,
                topic_code=topic_code,
                action=action,
                items=items,
                disclaimer=disclaimer,
                assistant_text=assistant_text,
                triage=triage,
                ui_cards=ui_cards,
            )

            await self.repo.commit()

        except Exception:
            await self.repo.rollback()
            raise

        return {
            "assistant_text": assistant_text,
            "triage": triage,
            "ui_cards": ui_cards,
            "retrieval": None,
        }