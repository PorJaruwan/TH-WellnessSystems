from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from app.api.v1.authen.auth import current_company_code
from app.api.v1.modules.ai.consult.dependencies import get_ai_topic_categories_service
from app.api.v1.modules.ai.consult.models._envelopes.ai_topic_category_envelopes import (
    AIConsultTopicCategoryListEnvelope,
    AIConsultTopicCategoryDetailEnvelope,
    AIConsultTopicCategoryCreateEnvelope,
    AIConsultTopicCategoryUpdateEnvelope,
    AIConsultTopicCategoryDeleteEnvelope,
    AIConsultTopicCategoryOptionsEnvelope,
    AIConsultTopicCategoryTreeEnvelope,
)

from app.api.v1.modules.ai.consult.models.ai_consult_topic_categories_schemas import (
    CreateAIConsultTopicCategoryRequest,
    UpdateAIConsultTopicCategoryRequest,
)
from app.api.v1.modules.ai.consult.services.ai_topic_categories_service import (
    AITopicCategoriesService,
)
from app.api.v1.utils.list_payload_builder import build_list_payload
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse

router = APIRouter()
# router = APIRouter(prefix="/topic-categories", tags=["AI_Consult_Topic"])


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicCategoryListEnvelope,
    response_model_exclude_none=True,
    operation_id="get_ai_consult_topic_categories",
)
async def get_ai_consult_topic_categories(
    service: AITopicCategoriesService = Depends(get_ai_topic_categories_service),
    company_code: str | None = Depends(current_company_code),
    is_active: bool | None = Query(default=None),
    q: str | None = Query(default=None),
    parent_category_id: UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    payload, total = await service.list_categories(
        company_code=company_code,
        is_active=is_active,
        q=q,
        parent_category_id=parent_category_id,
        limit=limit,
        offset=offset,
    )

    data = build_list_payload(
        items=payload.items,
        total=total,
        limit=limit,
        offset=offset,
        filters={
            "is_active": is_active,
            "q": q,
            "parent_category_id": str(parent_category_id) if parent_category_id else None,
        },
    ).model_dump(exclude_none=True)

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="AI consult topic categories retrieved successfully.",
        data=data,
    )


@router.get(
    "/options",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicCategoryOptionsEnvelope,
    response_model_exclude_none=True,
    operation_id="get_ai_consult_topic_category_options",
)
async def get_ai_consult_topic_category_options(
    service: AITopicCategoriesService = Depends(get_ai_topic_categories_service),
    company_code: str | None = Depends(current_company_code),
    is_active: bool | None = Query(default=True),
    parent_category_id: UUID | None = Query(default=None),
    lang: str = Query(default="th", description="th|en"),
):
    payload = await service.get_category_options(
        company_code=company_code,
        is_active=is_active,
        parent_category_id=parent_category_id,
        lang=lang,
    )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="AI consult topic category options retrieved successfully.",
        data=payload.model_dump(),
    )


@router.get(
    "/tree",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicCategoryTreeEnvelope,
    response_model_exclude_none=True,
    operation_id="get_ai_consult_topic_category_tree",
)
async def get_ai_consult_topic_category_tree(
    service: AITopicCategoriesService = Depends(get_ai_topic_categories_service),
    company_code: str | None = Depends(current_company_code),
    is_active: bool | None = Query(default=True),
):
    payload = await service.get_category_tree(
        company_code=company_code,
        is_active=is_active,
    )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="AI consult topic category tree retrieved successfully.",
        data=payload.model_dump(),
    )


@router.get(
    "/{category_id}",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicCategoryDetailEnvelope,
    response_model_exclude_none=True,
    operation_id="get_ai_consult_topic_category_by_id",
)
async def get_ai_consult_topic_category_by_id(
    category_id: UUID = Path(...),
    service: AITopicCategoriesService = Depends(get_ai_topic_categories_service),
    company_code: str | None = Depends(current_company_code),
):
    detail = await service.get_detail(
        category_id=category_id,
        company_code=company_code,
    )
    if not detail:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="AI consult topic category not found.",
            details={"category_id": str(category_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="AI consult topic category loaded successfully.",
        data=detail.model_dump(),
    )


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicCategoryCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_ai_consult_topic_category",
)
async def create_ai_consult_topic_category(
    body: CreateAIConsultTopicCategoryRequest,
    service: AITopicCategoriesService = Depends(get_ai_topic_categories_service),
    company_code: str | None = Depends(current_company_code),
):
    try:
        payload = await service.create_category(
            company_code=company_code,
            payload=body.model_dump(),
        )
    except ValueError as ex:
        if str(ex) == "CATEGORY_CODE_ALREADY_EXISTS":
            return ApiResponse.err(
                data_key="DUPLICATE",
                default_code="DATA_409",
                default_message="Category code already exists.",
                details={"category_code": body.category_code},
                status_code=409,
            )
        raise

    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message="AI consult topic category created successfully.",
        data=payload.model_dump(),
    )


@router.put(
    "/{category_id}",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicCategoryUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_ai_consult_topic_category",
)
async def update_ai_consult_topic_category(
    body: UpdateAIConsultTopicCategoryRequest,
    category_id: UUID = Path(...),
    service: AITopicCategoriesService = Depends(get_ai_topic_categories_service),
    company_code: str | None = Depends(current_company_code),
):
    try:
        detail = await service.update_category(
            category_id=category_id,
            company_code=company_code,
            payload=body.model_dump(exclude_unset=True),
        )
    except ValueError as ex:
        if str(ex) == "CATEGORY_CODE_ALREADY_EXISTS":
            return ApiResponse.err(
                data_key="DUPLICATE",
                default_code="DATA_409",
                default_message="Category code already exists.",
                details={
                    "category_id": str(category_id),
                    "category_code": body.category_code,
                },
                status_code=409,
            )
        raise

    if not detail:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="AI consult topic category not found.",
            details={"category_id": str(category_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="UPDATE_SUCCESS",
        default_message="AI consult topic category updated successfully.",
        data=detail.model_dump(),
    )


@router.delete(
    "/{category_id}",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultTopicCategoryDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_ai_consult_topic_category",
)
async def delete_ai_consult_topic_category(
    category_id: UUID = Path(...),
    service: AITopicCategoriesService = Depends(get_ai_topic_categories_service),
    company_code: str | None = Depends(current_company_code),
):
    try:
        payload = await service.delete_category(
            category_id=category_id,
            company_code=company_code,
        )
    except ValueError as ex:
        in_use_detail = service.parse_delete_error(ex)
        if in_use_detail:
            return ApiResponse.err(
                data_key="IN_USE",
                default_code="DATA_409",
                default_message="Cannot delete category because it is still used by AI topics.",
                details={
                    "category_id": str(category_id),
                    "topic_count": in_use_detail.get("topic_count", 0),
                    "sample_topics": in_use_detail.get("sample_topics", []),
                },
                status_code=409,
            )
        raise

    if not payload:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="AI consult topic category not found.",
            details={"category_id": str(category_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="DELETE_SUCCESS",
        default_message="AI consult topic category deleted successfully.",
        data=payload.model_dump(),
    )