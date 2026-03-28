from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from app.api.v1.authen.auth import current_company_code
from app.api.v1.modules.ai.consult.dependencies import get_ai_topic_services_service
from app.api.v1.modules.ai.consult.models._envelopes.ai_topic_service_envelopes import (
    AIConsultTopicServiceListEnvelope,
    AIConsultTopicServiceDetailEnvelope,
    AIConsultTopicServiceCreateEnvelope,
    AIConsultTopicServiceUpdateEnvelope,
    AIConsultTopicServiceDeleteEnvelope,
)
from app.api.v1.modules.ai.consult.models.ai_consult_topic_services_schemas import (
    CreateAIConsultTopicServiceRequest,
    UpdateAIConsultTopicServiceRequest,
)
from app.api.v1.modules.ai.consult.services.ai_topic_services_service import (
    AITopicServicesService,
)
from app.api.v1.utils.list_payload_builder import build_list_payload
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse

router = APIRouter()
# router = APIRouter(prefix="/topic-services", tags=["AI_Consult_Topic"])


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicServiceListEnvelope,
    response_model_exclude_none=True,
    operation_id="get_ai_consult_topic_services",
)
async def get_ai_consult_topic_services(
    service: AITopicServicesService = Depends(get_ai_topic_services_service),
    company_code: str | None = Depends(current_company_code),
    ai_topic_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    payload, total = await service.list_bindings(
        company_code=company_code,
        ai_topic_id=ai_topic_id,
        service_id=service_id,
        is_active=is_active,
        q=q,
        limit=limit,
        offset=offset,
    )

    data = build_list_payload(
        items=payload.items,
        total=total,
        limit=limit,
        offset=offset,
        filters={
            "ai_topic_id": str(ai_topic_id) if ai_topic_id else None,
            "service_id": str(service_id) if service_id else None,
            "is_active": is_active,
            "q": q,
        },
    ).model_dump(exclude_none=True)

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="AI consult topic services retrieved successfully.",
        data=data,
    )


@router.get(
    "/{binding_id}",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicServiceDetailEnvelope,
    response_model_exclude_none=True,
    operation_id="get_ai_consult_topic_service_by_id",
)
async def get_ai_consult_topic_service_by_id(
    binding_id: UUID = Path(...),
    service: AITopicServicesService = Depends(get_ai_topic_services_service),
    company_code: str | None = Depends(current_company_code),
):
    detail = await service.get_detail(binding_id=binding_id, company_code=company_code)
    if not detail:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="AI consult topic service not found.",
            details={"binding_id": str(binding_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="AI consult topic service loaded successfully.",
        data=detail.model_dump(),
    )


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicServiceCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_ai_consult_topic_service",
)
async def create_ai_consult_topic_service(
    body: CreateAIConsultTopicServiceRequest,
    service: AITopicServicesService = Depends(get_ai_topic_services_service),
    company_code: str | None = Depends(current_company_code),
):
    try:
        payload = await service.create_binding(
            company_code=company_code,
            payload=body.model_dump(),
        )
    except ValueError as ex:
        if str(ex) == "AI_TOPIC_NOT_FOUND":
            return ApiResponse.err(
                data_key="NOT_FOUND",
                default_code="DATA_001",
                default_message="AI topic not found.",
                details={"ai_topic_id": str(body.ai_topic_id)},
                status_code=404,
            )
        if str(ex) == "SERVICE_NOT_FOUND":
            return ApiResponse.err(
                data_key="NOT_FOUND",
                default_code="DATA_001",
                default_message="Service not found.",
                details={"service_id": str(body.service_id)},
                status_code=404,
            )
        if str(ex) == "TOPIC_SERVICE_ALREADY_EXISTS":
            return ApiResponse.err(
                data_key="DUPLICATE",
                default_code="DATA_409",
                default_message="AI topic service already exists.",
                details={
                    "ai_topic_id": str(body.ai_topic_id),
                    "service_id": str(body.service_id),
                },
                status_code=409,
            )
        raise

    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message="AI consult topic service created successfully.",
        data=payload.model_dump(),
    )


@router.put(
    "/{binding_id}",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicServiceUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_ai_consult_topic_service",
)
async def update_ai_consult_topic_service(
    body: UpdateAIConsultTopicServiceRequest,
    binding_id: UUID = Path(...),
    service: AITopicServicesService = Depends(get_ai_topic_services_service),
    company_code: str | None = Depends(current_company_code),
):
    detail = await service.update_binding(
        binding_id=binding_id,
        company_code=company_code,
        payload=body.model_dump(exclude_unset=True),
    )
    if not detail:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="AI consult topic service not found.",
            details={"binding_id": str(binding_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="UPDATE_SUCCESS",
        default_message="AI consult topic service updated successfully.",
        data=detail.model_dump(),
    )


@router.delete(
    "/{binding_id}",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicServiceDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_ai_consult_topic_service",
)
async def delete_ai_consult_topic_service(
    binding_id: UUID = Path(...),
    service: AITopicServicesService = Depends(get_ai_topic_services_service),
    company_code: str | None = Depends(current_company_code),
):
    payload = await service.delete_binding(
        binding_id=binding_id,
        company_code=company_code,
    )
    if not payload:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="AI consult topic service not found.",
            details={"binding_id": str(binding_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="DELETE_SUCCESS",
        default_message="AI consult topic service deleted successfully.",
        data=payload.model_dump(),
    )