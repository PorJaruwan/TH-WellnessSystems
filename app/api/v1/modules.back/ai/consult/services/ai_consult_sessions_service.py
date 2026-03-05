# app/api/v1/modules/ai/consult/services/ai_consult_sessions_service.py

from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from app.api.v1.modules.ai.consult.repositories.ai_consult_sessions_repository import (
    AIConsultSessionsRepository,
)
from app.api.v1.modules.ai.consult.models.dtos import (
    AIConsultSessionItem,
    AIConsultSessionsListPayload,
    AIConsultSessionDetailPayload,
)


class AIConsultSessionsService:
    """Use-case layer for listing and fetching AI consult sessions (masters-style)."""

    def __init__(self, repo: AIConsultSessionsRepository):
        self.repo = repo

    @staticmethod
    def _entry_point_from_meta(meta: Any) -> str | None:
        if isinstance(meta, dict):
            return meta.get("entry_point")
        return None

    async def list_my_sessions(
        self,
        *,
        company_code: str,
        patient_id: str,
        status: str = "active",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[AIConsultSessionsListPayload, int]:
        rows, total = await self.repo.list_patient_sessions(
            company_code=company_code,
            patient_id=patient_id,
            status=status,
            limit=limit,
            offset=offset,
        )

        items: list[AIConsultSessionItem] = []
        for s in rows:
            meta = getattr(s, "meta", None) or getattr(s, "metadata", None) or {}
            items.append(
                AIConsultSessionItem(
                    session_id=str(s.id),
                    company_code=s.company_code,
                    patient_id=str(s.patient_id) if s.patient_id else None,
                    topic_code=getattr(s, "topic_code", None),
                    language=getattr(s, "language", None),
                    status=s.status,
                    last_activity_at=s.last_activity_at.isoformat() if s.last_activity_at else None,
                    created_at=s.created_at.isoformat() if s.created_at else None,
                    entry_point=self._entry_point_from_meta(meta),
                )
            )

        return AIConsultSessionsListPayload(items=items), int(total)

    async def get_session_detail(
        self,
        *,
        company_code: str,
        patient_id: str,
        session_id: UUID,
    ) -> AIConsultSessionDetailPayload | None:
        row = await self.repo.get_patient_session(
            company_code=company_code,
            patient_id=patient_id,
            session_id=session_id,
        )
        if not row:
            return None

        meta = getattr(row, "meta", None) or getattr(row, "metadata", None) or {}
        return AIConsultSessionDetailPayload(
            session_id=str(row.id),
            company_code=row.company_code,
            patient_id=str(row.patient_id) if row.patient_id else None,
            staff_id=str(getattr(row, "staff_id", "")) if getattr(row, "staff_id", None) else None,
            topic_code=getattr(row, "topic_code", None),
            language=getattr(row, "language", None),
            status=row.status,
            last_activity_at=row.last_activity_at.isoformat() if row.last_activity_at else None,
            created_at=row.created_at.isoformat() if row.created_at else None,
            entry_point=self._entry_point_from_meta(meta),
            triage_level=getattr(row, "triage_level", None),
            triage_reason=getattr(row, "triage_reason", None),
            app_context=getattr(row, "app_context", None),
            channel=getattr(row, "channel", None),
        )
