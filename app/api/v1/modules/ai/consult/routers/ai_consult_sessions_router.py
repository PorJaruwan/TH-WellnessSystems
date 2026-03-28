from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse

from app.api.v1.authen.auth import current_company_code, current_patient_id
from app.api.v1.modules.ai.consult.dependencies import get_ai_consult_sessions_service
from app.api.v1.modules.ai.consult.models._envelopes.ai_consult_envelopes import (
    AIConsultSessionEnvelope,
    AIConsultSessionsListEnvelope,
    AIConsultSessionDetailEnvelope,
)
from app.api.v1.modules.ai.consult.models.dtos import (
    CreateAIConsultSessionPayload,
)
from app.api.v1.modules.ai.consult.models.schemas import (
    CreateAIConsultSessionRequest,
)
from app.api.v1.modules.ai.consult.services.ai_consult_service import (
    create_or_get_ai_consult_session,
)
from app.api.v1.modules.ai.consult.services.ai_consult_sessions_service import (
    AIConsultSessionsService,
)
from app.api.v1.utils.list_payload_builder import build_list_payload

router = APIRouter()
# router = APIRouter(prefix="/sessions", tags=["AI Consult Sessions"])


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
        details={"hint": "patient_id is required for patient AI consult"},
        status_code=403,
    )


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultSessionEnvelope,
    response_model_exclude_none=True,
    operation_id="create_ai_consult_session",
)
async def create_session(
    body: CreateAIConsultSessionRequest,
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    if not company_code:
        return _unauthorized_company_code()
    if not patient_id:
        return _forbidden_patient_id()

    language = body.language or "th-TH"
    entry_point = body.entry_point or "pre_consult"

    row, flag = await create_or_get_ai_consult_session(
        db,
        company_code=company_code,
        patient_id=patient_id,
        topic_code=body.topic_code,
        language=language,
        entry_point=entry_point,
    )

    if flag == "TOPIC_NOT_FOUND":
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Data not found.",
            details={"topic_code": body.topic_code},
            status_code=404,
        )

    if not row or flag == "CREATE_FAILED":
        return ApiResponse.err(
            data_key="CREATE_FAILED",
            default_code="DATA_004",
            default_message="Create failed.",
            details={"hint": "insert chat_sessions failed"},
            status_code=500,
        )

    payload = CreateAIConsultSessionPayload(
        session_id=row["session_id"],
        company_code=row["company_code"],
        patient_id=row["patient_id"],
    ).model_dump()

    message = (
        "Session reused successfully."
        if flag == "REUSED"
        else "Session created successfully."
    )

    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message=message,
        data=payload,
    )


@router.get(
    "/my",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultSessionsListEnvelope,
    response_model_exclude_none=True,
    operation_id="get_my_ai_consult_sessions",
)
async def get_my_sessions(
    service: AIConsultSessionsService = Depends(get_ai_consult_sessions_service),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
    status: str = Query(default="active", description="active|closed|all"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    if not company_code:
        return _unauthorized_company_code()
    if not patient_id:
        return _forbidden_patient_id()

    payload, total = await service.list_my_sessions(
        company_code=company_code,
        patient_id=patient_id,
        status=status,
        limit=limit,
        offset=offset,
    )

    data = build_list_payload(
        items=payload.items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"status": status},
    ).model_dump(exclude_none=True)

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Retrieved successfully.",
        data=data,
    )


@router.get(
    "/{session_id}",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultSessionDetailEnvelope,
    response_model_exclude_none=True,
    operation_id="get_ai_consult_session_by_id",
)
async def get_session_detail(
    session_id: UUID = Path(...),
    service: AIConsultSessionsService = Depends(get_ai_consult_sessions_service),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    if not company_code:
        return _unauthorized_company_code()
    if not patient_id:
        return _forbidden_patient_id()

    detail = await service.get_session_detail(
        company_code=company_code,
        patient_id=patient_id,
        session_id=session_id,
    )

    if not detail:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Session not found.",
            details={"session_id": str(session_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Session loaded successfully.",
        data=detail.model_dump(),
    )