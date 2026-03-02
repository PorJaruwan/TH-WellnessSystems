from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.chat.models.schemas import ChatEscalationUpdateRequest


class ChatEscalationsService:
    """SQL-based service for chat escalations.

    Masters-style DI:
    - db injected once in __init__
    - methods do NOT accept db parameter
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_my_escalations(
        self,
        company_code: str,
        patient_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Dict[str, Any]], int]:
        base_sql = """
        FROM public.chat_escalations
        WHERE company_code = :company_code
          AND patient_id = :patient_id
        """

        params: Dict[str, Any] = {
            "company_code": company_code,
            "patient_id": str(patient_id),
        }

        if status:
            base_sql += " AND status = :status"
            params["status"] = status

        count_stmt = text("SELECT COUNT(1) " + base_sql)
        total = (await self.db.execute(count_stmt, params)).scalar_one() or 0

        data_sql = """
        SELECT
          id, company_code, session_id, patient_id,
          status, reason,
          assigned_staff_id, booking_id,
          created_at, updated_at
        """ + base_sql + """
        ORDER BY updated_at DESC NULLS LAST, created_at DESC
        LIMIT :limit OFFSET :offset
        """

        params.update({"limit": limit, "offset": offset})
        rows = (await self.db.execute(text(data_sql), params)).mappings().all()
        return [dict(r) for r in rows], int(total)

    async def get_escalation_by_id(
        self,
        company_code: str,
        escalation_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        stmt = text(
            """
            SELECT
              id, company_code, session_id, patient_id,
              status, reason,
              assigned_staff_id, booking_id,
              created_at, updated_at, resolution_note, metadata
            FROM public.chat_escalations
            WHERE company_code = :company_code
              AND id = :id
            """
        )
        row = (
            await self.db.execute(
                stmt, {"company_code": company_code, "id": str(escalation_id)}
            )
        ).mappings().first()
        return dict(row) if row else None

    async def update_escalation(
        self,
        company_code: str,
        escalation_id: UUID,
        req: ChatEscalationUpdateRequest,
    ) -> Optional[Dict[str, Any]]:
        # Build dynamic SET clause
        sets: list[str] = []
        params: Dict[str, Any] = {"company_code": company_code, "id": str(escalation_id)}

        if req.status is not None:
            sets.append("status = :status")
            params["status"] = req.status
        if req.assigned_staff_id is not None:
            sets.append("assigned_staff_id = :assigned_staff_id")
            params["assigned_staff_id"] = str(req.assigned_staff_id)
        if req.booking_id is not None:
            sets.append("booking_id = :booking_id")
            params["booking_id"] = str(req.booking_id)
        if req.resolution_note is not None:
            sets.append("resolution_note = :resolution_note")
            params["resolution_note"] = req.resolution_note
        if req.metadata is not None:
            sets.append("metadata = :metadata::jsonb")
            params["metadata"] = req.metadata

        if not sets:
            return await self.get_escalation_by_id(company_code=company_code, escalation_id=escalation_id)

        stmt = text(
            """
            UPDATE public.chat_escalations
            SET """ + ", ".join(sets) + ", updated_at = NOW()\n" + """
            WHERE company_code = :company_code
              AND id = :id
            RETURNING
              id, company_code, session_id, patient_id,
              status, reason,
              assigned_staff_id, booking_id,
              created_at, updated_at, resolution_note, metadata
            """
        )
        row = (await self.db.execute(stmt, params)).mappings().first()
        return dict(row) if row else None
