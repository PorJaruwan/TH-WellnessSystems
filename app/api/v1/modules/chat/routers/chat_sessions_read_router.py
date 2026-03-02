from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.utils.list_payload_builder import build_list_payload
from app.api.v1.authen.auth import current_company_code, current_patient_id
from app.api.v1.modules.chat.utils.auth_guards import guard_patient_chat

from app.api.v1.modules.chat.models._envelopes.chat_envelopes import (
    ChatSessionHeaderEnvelope,
    ChatMessagesEnvelope,
)
from app.api.v1.modules.chat.services.chat_service import (
    get_chat_session_header,
    list_chat_messages,
)


router = APIRouter()



# GET /api/v1/chat/sessions/{session_id}
@router.get(
    "/{session_id}",
    response_class=UnicodeJSONResponse,
    response_model=ChatSessionHeaderEnvelope,
    response_model_exclude_none=True,
)
async def get_session(
    session_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard
    data = await get_chat_session_header(
        db,
        company_code=company_code,
        patient_id=patient_id,
        session_id=session_id,
    )
    if not data:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Session not found.",
            details={"session_id": str(session_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Session header loaded successfully.",
        data={"item": data},
    )


# GET /api/v1/chat/sessions/{session_id}/messages
@router.get(
    "/{session_id}/messages",
    response_class=UnicodeJSONResponse,
    response_model=ChatMessagesEnvelope,
    response_model_exclude_none=True,
)
async def get_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    before: datetime | None = Query(default=None, description="ISO datetime"),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard
    items, total = await list_chat_messages(
        db,
        company_code=company_code,
        patient_id=patient_id,
        session_id=session_id,
        limit=limit,
        offset=offset,
        before=before,
    )

    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"before": before},
    )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Messages loaded successfully.",
        data=payload.model_dump(exclude_none=True),
    )



