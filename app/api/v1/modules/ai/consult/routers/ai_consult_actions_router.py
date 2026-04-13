from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path

from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse

from app.api.v1.authen.auth import current_company_code, current_patient_id
from app.api.v1.modules.ai.consult.dependencies import get_ai_consult_actions_service
from app.api.v1.modules.ai.consult.models.schemas import AIQuickActionRequest
from app.api.v1.modules.ai.consult.services.ai_consult_actions_service import (
    AIConsultActionsService,
)
from app.api.v1.modules.chat.models._envelopes.chat_envelopes import (
    ChatSendMessageEnvelope,
)

router = APIRouter()


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
        details={"hint": "patient_id is required"},
        status_code=403,
    )


@router.post(
    "/{session_id}/quick",
    response_class=UnicodeJSONResponse,
    response_model=ChatSendMessageEnvelope,
    response_model_exclude_none=True,
    operation_id="quick_action_ai_consult_session",
)
async def quick_action(
    body: AIQuickActionRequest,
    session_id: UUID = Path(...),
    service: AIConsultActionsService = Depends(get_ai_consult_actions_service),
    company_code: str | None = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    if not company_code:
        return _unauthorized_company_code()

    if not patient_id:
        return _forbidden_patient_id()

    result = await service.run_quick_action(
        company_code=company_code,
        patient_id=patient_id,
        session_id=session_id,
        action=body.action,
        lang=body.lang,
    )

    if result == "SESSION_NOT_FOUND":
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Session not found.",
            details={"session_id": str(session_id)},
            status_code=404,
        )

    if result == "TOPIC_NOT_SET":
        return ApiResponse.err(
            data_key="INVALID",
            default_code="DATA_002",
            default_message="Topic not set on session.",
            details={"session_id": str(session_id)},
            status_code=400,
        )

    if result == "TOPIC_NOT_FOUND":
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Topic not found.",
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message="Quick action completed successfully.",
        data=result,
    )