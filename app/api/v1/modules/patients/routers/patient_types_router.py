from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.patients.models.schemas import PatientTypeCreate, PatientTypeUpdate
from app.api.v1.modules.patients.models.dtos import PatientTypeDTO
from app.api.v1.modules.patients.models._envelopes.patient_types_envelopes import (
    PatientTypeSingleEnvelope,
    PatientTypeListEnvelope,
    PatientTypeDeleteEnvelope,
)

from app.api.v1.modules.patients.repositories.masterdata_repository import MasterDataRepository
from app.api.v1.modules.patients.services.masterdata_service import MasterDataService
from app.db.models.patient_settings import PatientType


router = APIRouter()

DEFAULT_SORT_BY = "type_name"
ALLOWED_SORT_FIELDS = ["type_name", "description", "created_at", "updated_at", "is_active"]
SEARCH_FIELDS = ["type_name", "description"]


def get_masterdata_service(db: AsyncSession = Depends(get_db)) -> MasterDataService:
    return MasterDataService(MasterDataRepository(db))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=PatientTypeSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="create_patient_type",
)
async def create_patient_type(request: Request, payload: PatientTypeCreate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.create(PatientType, payload.model_dump())
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": PatientTypeDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=PatientTypeListEnvelope,
    response_model_exclude_none=True,
    operation_id="search_patient_types",
)
async def search_patient_types(
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
        model=PatientType,
        dto=PatientTypeDTO,
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
    "/{patient_type_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientTypeSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="read_patient_type",
)
async def read_patient_type(request: Request, patient_type_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    item = await repo.get_by_id(PatientType, patient_type_id)
    if item is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(patient_type_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": PatientTypeDTO.model_validate(item).model_dump(exclude_none=True)},
    )


@router.put(
    "/{patient_type_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientTypeSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="update_patient_type",
)
async def update_patient_type(
    request: Request, patient_type_id: UUID, payload: PatientTypeUpdate, db: AsyncSession = Depends(get_db)
):
    repo = MasterDataRepository(db)
    obj = await repo.update_by_id(PatientType, patient_type_id, payload.model_dump(exclude_unset=True))
    if obj is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(patient_type_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": PatientTypeDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/{patient_type_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=PatientTypeDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_patient_type",
)
async def delete_patient_type(request: Request, patient_type_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    deleted = await repo.delete_by_id(PatientType, patient_type_id)
    if not deleted:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(patient_type_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=f"PatientType with id {patient_type_id} deleted.",
        data={"deleted": True, "id": str(patient_type_id)},
    )