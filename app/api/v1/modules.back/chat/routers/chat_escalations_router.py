from __future__ import annotations

from fastapi import APIRouter, Depends, Path
from uuid import UUID

from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse

from app.api.v1.authen.auth import current_company_code, current_patient_id
from app.api.v1.modules.chat.dependencies import get_chat_escalations_service
from app.api.v1.modules.chat.services.chat_escalations_service import ChatEscalationsService
from app.api.v1.modules.chat.models.schemas import ChatEscalationUpdateRequest
from app.api.v1.modules.chat.models._envelopes.chat_escalations_envelopes import ChatEscalationEnvelope


router = APIRouter()


# PATCH /api/v1/chat/escalations/{id}
@router.patch(
    "/{escalation_id}",
    response_class=UnicodeJSONResponse,
    response_model=ChatEscalationEnvelope,
    response_model_exclude_none=True,
)
async def update_escalation(
    escalation_id: UUID = Path(...),
    escalations_service: ChatEscalationsService = Depends(get_chat_escalations_service),
    req: ChatEscalationUpdateRequest = ...,
    company_code: str = Depends(current_company_code),
    patient_id: UUID = Depends(current_patient_id),
):
    try:
        data = await escalations_service.update_escalation(
                        company_code=company_code,
            escalation_id=escalation_id,
            req=req,
            patient_id=patient_id,
            is_staff=False,
        )
        return ApiResponse.ok(
            success_key="UPDATE_SUCCESS",
            default_message="Escalation updated successfully.",
            data={"item": data},
        )
    except ValueError as e:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_404",
            default_message=str(e),
            details={"escalation_id": str(escalation_id)},
            status_code=404,
        )
