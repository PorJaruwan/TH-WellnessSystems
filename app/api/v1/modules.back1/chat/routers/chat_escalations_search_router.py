from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from uuid import UUID

from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.authen.auth import current_company_code, current_patient_id
from app.api.v1.modules.chat.dependencies import get_chat_escalations_service
from app.api.v1.modules.chat.services.chat_escalations_service import ChatEscalationsService
from app.api.v1.modules.chat.models._envelopes.chat_escalations_envelopes import ChatEscalationsEnvelope


router = APIRouter()


@router.get(
    "/my",
    response_class=UnicodeJSONResponse,
    response_model=ChatEscalationsEnvelope,
    response_model_exclude_none=True,
    operation_id="search_my_escalations",
)
async def search_my_escalations(
    status: str | None = Query(default=None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    escalations_service: ChatEscalationsService = Depends(get_chat_escalations_service),
    company_code: str = Depends(current_company_code),
    patient_id: UUID = Depends(current_patient_id),
):
    rows, total = await escalations_service.list_my_escalations(
                company_code=company_code,
        patient_id=patient_id,
        status=status,
        limit=limit,
        offset=offset,
    )

    payload = build_list_payload(
        items=rows,
        total=total,
        limit=limit,
        offset=offset,
        filters={"status": status},
    )
    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Escalations loaded successfully.",
        data=payload.model_dump(exclude_none=True),
    )
