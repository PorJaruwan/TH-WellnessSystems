from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.utils.list_payload_builder import build_list_payload
from app.api.v1.authen.auth import current_company_code, current_patient_id
from app.api.v1.modules.chat.utils.auth_guards import guard_patient_chat

from app.api.v1.modules.chat.models._envelopes.chat_envelopes import ChatSessionSummaryListEnvelope
from app.api.v1.modules.chat.models.dtos import ChatSessionSummaryItem
from app.api.v1.modules.chat.services.chat_service import ChatService


router = APIRouter()



# GET /api/v1/chat/sessions/my?status=open
@router.get(
    "/my",
    response_class=UnicodeJSONResponse,
    response_model=ChatSessionSummaryListEnvelope,
    response_model_exclude_none=True,
    operation_id="search_my_sessions",
)
async def search_my_sessions(
    status: str = Query(default="open", description="open|closed"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard
    rows, total = await ChatService.list_my_sessions(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
        status=status,
        limit=limit,
        offset=offset,
    )

    items: list[ChatSessionSummaryItem] = []
    for r in rows:
        items.append(
            ChatSessionSummaryItem(
                session_id=r.get("session_id") or r.get("id"),
                status=r.get("status"),
                last_activity_at=r.get("last_activity_at"),
                created_at=r.get("created_at"),
                title=r.get("title"),
                topic_code=r.get("topic_code") or r.get("topic"),
                last_message_at=r.get("last_message_at"),
                last_message=r.get("last_message") or r.get("last_message_text"),
            )
        )

    payload = build_list_payload(
        items=[i.model_dump() for i in items],
        total=total,
        limit=limit,
        offset=offset,
        filters={"status": status},
    )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Sessions loaded successfully.",
        data=payload.model_dump(exclude_none=True),
    )
