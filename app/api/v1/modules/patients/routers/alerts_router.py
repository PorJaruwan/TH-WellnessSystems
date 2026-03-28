# app\api\v1\modules\patients\routers\alerts_router.py
from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.patients.models.schemas import AlertCreate, AlertUpdate
from app.api.v1.modules.patients.models.dtos import AlertDTO
from app.api.v1.modules.patients.models._envelopes.alerts_envelopes import (
    AlertSingleEnvelope,
    AlertListEnvelope,
    AlertDeleteEnvelope,
)

from app.api.v1.modules.patients.repositories.masterdata_repository import MasterDataRepository
from app.api.v1.modules.patients.services.masterdata_service import MasterDataService
from app.db.models.patient_settings import Alert


router = APIRouter()

DEFAULT_SORT_BY = "alert_name"
ALLOWED_SORT_FIELDS = ["alert_name", "alert_type", "description", "created_at", "updated_at", "is_active"]
SEARCH_FIELDS = ["alert_name", "alert_type", "description"]


def get_masterdata_service(db: AsyncSession = Depends(get_db)) -> MasterDataService:
    return MasterDataService(MasterDataRepository(db))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=AlertSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="create_alert",
)
async def create_alert(request: Request, payload: AlertCreate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.create(Alert, payload.model_dump())
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": AlertDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=AlertListEnvelope,
    response_model_exclude_none=True,
    operation_id="search_alerts",
)
async def search_alerts(
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
        model=Alert,
        dto=AlertDTO,
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
        message=ResponseCode.SUCCESS["LISTED"][1],
        data=payload.model_dump(exclude_none=True),
    )


@router.get(
    "/{alert_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AlertSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="read_alert",
)
async def read_alert(request: Request, alert_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    item = await repo.get_by_id(Alert, alert_id)
    if item is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(alert_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": AlertDTO.model_validate(item).model_dump(exclude_none=True)},
    )


@router.put(
    "/{alert_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AlertSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="update_alert",
)
async def update_alert(request: Request, alert_id: UUID, payload: AlertUpdate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.update_by_id(Alert, alert_id, payload.model_dump(exclude_unset=True))
    if obj is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(alert_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": AlertDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/{alert_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AlertDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_alert",
)
async def delete_alert(request: Request, alert_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    deleted = await repo.delete_by_id(Alert, alert_id)
    if not deleted:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(alert_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=f"Alert with id {alert_id} deleted.",
        data={"deleted": True, "id": str(alert_id)},
    )