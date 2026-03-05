from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.authen.auth import current_company_code, current_patient_id
from app.api.v1.modules.chat.utils.auth_guards import guard_patient_chat

from app.api.v1.modules.chat.models._envelopes.chat_envelopes import (
    ChatCreateSessionEnvelope,
    ChatSendMessageEnvelope,
    ChatSessionHeaderEnvelope,
)
from app.api.v1.modules.chat.models.schemas import ChatCreateSessionRequest, ChatSendMessageRequest
from app.api.v1.modules.chat.dependencies import get_chat_service
from app.api.v1.modules.chat.services.chat_service import ChatService, close_chat_session, send_chat_message


router = APIRouter()



# POST /api/v1/chat/sessions
@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=ChatCreateSessionEnvelope,
    response_model_exclude_none=True,
)
async def create_session(
    body: ChatCreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    chat_service = Depends(get_chat_service),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard

    data = await chat_service.create_session(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
        topic_code=body.topic_code,
        language=body.language,
        channel=body.channel,
        reuse_open=body.reuse_open,
    )

    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message="Session created successfully.",
        data={"item": data},
    )


# POST /api/v1/chat/sessions/{session_id}/messages
@router.post(
    "/{session_id}/messages",
    response_class=UnicodeJSONResponse,
    response_model=ChatSendMessageEnvelope,
    response_model_exclude_none=True,
)
async def post_message(
    body: ChatSendMessageRequest,
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    chat_service = Depends(get_chat_service),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard

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

    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message="Message sent successfully.",
        data={"item": result},
    )


# POST /api/v1/chat/sessions/{session_id}/close
@router.post(
    "/{session_id}/close",
    response_class=UnicodeJSONResponse,
    response_model=ChatSessionHeaderEnvelope,
    response_model_exclude_none=True,
)
async def close_session(
    session_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    chat_service = Depends(get_chat_service),
    company_code: str | None = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard

    data = await close_chat_session(
        db,
        company_code=company_code,
        patient_id=patient_id,
        session_id=session_id,
    )
    if not data:
        return ApiResponse.err(
            data_key="INVALID",
            default_code="DATA_404",
            default_message="Not found.",
            details={"hint": "session not found"},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="UPDATE_SUCCESS",
        default_message="Session closed.",
        data={"item": data},
    )


# POST /api/v1/chat/sessions/{session_id}/reopen
@router.post(
    "/{session_id}/reopen",
    response_class=UnicodeJSONResponse,
    response_model=ChatSessionHeaderEnvelope,
    response_model_exclude_none=True,
)
async def reopen_session(
    session_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    chat_service = Depends(get_chat_service),
    company_code: str | None = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard

    data = await ChatService.reopen_session(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
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
        success_key="UPDATE_SUCCESS",
        default_message="Session reopened.",
        data={"item": data},
    )



