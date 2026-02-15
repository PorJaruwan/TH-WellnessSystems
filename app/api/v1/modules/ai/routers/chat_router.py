# app/api/v1/modules/ai/routers/chat_router.py

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.users.auth import current_company_code, current_patient_id

from app.api.v1.modules.ai.schemas.envelopes.chat_envelopes import (
    ChatSessionHeaderEnvelope,
    ChatMessagesEnvelope,
    ChatSendMessageEnvelope,
)
from app.api.v1.modules.ai.schemas.chat_model import ChatSendMessageRequest, ChatSendMessagePayload
from app.api.v1.modules.ai.services.chat_service import (
    get_chat_session_header,
    list_chat_messages,
    send_chat_message,
)

router = APIRouter(prefix="/chat", tags=["AI_Chat"])

router = APIRouter(
    prefix="/ai/chat",
    tags=["AI_Consult"],
)

def _unauthorized_company_code():
    return ApiResponse.err(
        data_key="INVALID",
        default_code="AUTH_401",
        default_message="Unauthorized",
        details={"hint": "company_code is null"},
        status_code=401,
    )


def _forbidden_patient_id():
    return ApiResponse.err(
        data_key="INVALID",
        default_code="AUTH_403",
        default_message="Forbidden",
        details={"hint": "patient_id is required for patient chat"},
        status_code=403,
    )


# 4) GET /api/v1/chat/sessions/{session_id}
@router.get(
    "/sessions/{session_id}",
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
    if not company_code:
        return _unauthorized_company_code()
    if not patient_id:
        return _forbidden_patient_id()

    data = await get_chat_session_header(db, company_code=company_code, patient_id=patient_id, session_id=session_id)
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
        data=data,
    )


# 5) GET /api/v1/chat/sessions/{session_id}/messages?limit=50&before=...
@router.get(
    "/sessions/{session_id}/messages",
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
    before: datetime | None = Query(default=None, description="ISO datetime"),
):
    if not company_code:
        return _unauthorized_company_code()
    if not patient_id:
        return _forbidden_patient_id()

    items = await list_chat_messages(
        db,
        company_code=company_code,
        patient_id=patient_id,
        session_id=session_id,
        limit=limit,
        before=before,
    )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Messages loaded successfully.",
        data={"items": items, "limit": limit, "before": before},
    )


# 6) POST /api/v1/chat/sessions/{session_id}/messages
@router.post(
    "/sessions/{session_id}/messages",
    response_class=UnicodeJSONResponse,
    response_model=ChatSendMessageEnvelope,
    response_model_exclude_none=True,
)
async def post_message(
    body: ChatSendMessageRequest,
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    if not company_code:
        return _unauthorized_company_code()
    if not patient_id:
        return _forbidden_patient_id()

    result = await send_chat_message(
        db,
        company_code=company_code,
        patient_id=patient_id,
        session_id=session_id,
        text=body.text,
    )

    if result == "SESSION_NOT_FOUND":
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Session not found.",
            details={"session_id": str(session_id)},
            status_code=404,
        )

    payload = ChatSendMessagePayload(**result).model_dump()
    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message="Message sent successfully.",
        data=payload,
    )
