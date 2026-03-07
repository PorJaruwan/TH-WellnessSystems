from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.patients.models.schemas import SourceCreate, SourceUpdate
from app.api.v1.modules.patients.models.dtos import SourceDTO
from app.api.v1.modules.patients.models._envelopes.sources_envelopes import (
    SourceSingleEnvelope,
    SourceListEnvelope,
    SourceDeleteEnvelope,
)

from app.api.v1.modules.patients.repositories.masterdata_repository import MasterDataRepository
from app.api.v1.modules.patients.services.masterdata_service import MasterDataService
from app.db.models.patient_settings import Source


router = APIRouter()

DEFAULT_SORT_BY = "source_name"
ALLOWED_SORT_FIELDS = ["source_name", "source_type", "description", "created_at", "updated_at", "is_active"]
SEARCH_FIELDS = ["source_name", "source_type", "description"]


def get_masterdata_service(db: AsyncSession = Depends(get_db)) -> MasterDataService:
    return MasterDataService(MasterDataRepository(db))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=SourceSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="create_source",
)
async def create_source(request: Request, payload: SourceCreate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.create(Source, payload.model_dump())
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": SourceDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=SourceListEnvelope,
    response_model_exclude_none=True,
    operation_id="search_sources",
)
async def search_sources(
    request: Request,
    q: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort_by: str = Query(DEFAULT_SORT_BY),
    sort_order: str = Query("asc"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: MasterDataService = Depends(get_masterdata_service),
):
    payload, _, _ = await svc.search_list_payload(
        model=Source,
        dto=SourceDTO,
        q=q,
        is_active=is_active,
        search_fields=SEARCH_FIELDS,
        sort_by=sort_by,
        sort_order=sort_order,
        allowed_sort_fields=ALLOWED_SORT_FIELDS,
        default_sort_by=DEFAULT_SORT_BY,
        limit=limit,
        offset=offset,
        filters_payload={"q": q, "is_active": is_active},
    )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )


@router.get(
    "/{source_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SourceSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="read_source",
)
async def read_source(request: Request, source_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    item = await repo.get_by_id(Source, source_id)
    if item is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(source_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": SourceDTO.model_validate(item).model_dump(exclude_none=True)},
    )


@router.put(
    "/{source_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SourceSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="update_source",
)
async def update_source(request: Request, source_id: UUID, payload: SourceUpdate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.update_by_id(Source, source_id, payload.model_dump(exclude_unset=True))
    if obj is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(source_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": SourceDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/{source_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SourceDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_source",
)
async def delete_source(request: Request, source_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    deleted = await repo.delete_by_id(Source, source_id)
    if not deleted:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(source_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=f"Source with id {source_id} deleted.",
        data={"deleted": True, "id": str(source_id)},
    )