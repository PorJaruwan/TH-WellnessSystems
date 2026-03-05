from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path

from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.authen.auth import current_company_code

from app.api.v1.modules.chat.dependencies import get_chat_retrievals_service
from app.api.v1.modules.chat.services.chat_retrievals_service import ChatRetrievalsService
from app.api.v1.modules.chat.models._envelopes.chat_retrievals_envelopes import ChatRetrievalDetailEnvelope


router = APIRouter()


# GET /api/v1/chat/retrievals/{id}
@router.get(
    "/{retrieval_id}",
    response_class=UnicodeJSONResponse,
    response_model=ChatRetrievalDetailEnvelope,
    response_model_exclude_none=True,
)
async def get_retrieval_detail(
    retrieval_id: UUID = Path(...),
    retrievals_service: ChatRetrievalsService = Depends(get_chat_retrievals_service),
    company_code: str = Depends(current_company_code),
):
    try:
        item = await retrievals_service.get_retrieval_detail(
                        company_code=company_code,
            retrieval_id=retrieval_id,
        )
        return ApiResponse.ok(
            success_key="GET_SUCCESS",
            default_message="Retrieval loaded.",
            data={"item": item.model_dump()},
        )
    except ValueError as e:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_404",
            default_message=str(e),
            details={"retrieval_id": str(retrieval_id)},
            status_code=404,
        )
