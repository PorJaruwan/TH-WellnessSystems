from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.modules.patients.models.schemas import AllergyCreate, AllergyUpdate
from app.api.v1.modules.patients.models.dtos import AllergyDTO
from app.api.v1.modules.patients.models._envelopes.allergies_envelopes import (
    AllergySingleEnvelope,
    AllergyListEnvelope,
    AllergyDeleteEnvelope,
)

from app.api.v1.modules.patients.repositories.masterdata_repository import MasterDataRepository
from app.api.v1.modules.patients.services.masterdata_service import MasterDataService
from app.db.models.patient_settings import Allergy


router = APIRouter()

DEFAULT_SORT_BY = "allergy_name"
ALLOWED_SORT_FIELDS = ["allergy_name", "allergy_type", "description", "created_at", "updated_at", "is_active"]
SEARCH_FIELDS = ["allergy_name", "allergy_type", "description"]


def get_masterdata_service(db: AsyncSession = Depends(get_db)) -> MasterDataService:
    return MasterDataService(MasterDataRepository(db))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=AllergySingleEnvelope,
    response_model_exclude_none=True,
    operation_id="create_allergy",
)
async def create_allergy(request: Request, payload: AllergyCreate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.create(Allergy, clean_create(payload))
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": AllergyDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=AllergyListEnvelope,
    response_model_exclude_none=True,
    operation_id="search_allergies",
)
async def search_allergies(
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
        model=Allergy,
        dto=AllergyDTO,
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
    "/{allergy_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AllergySingleEnvelope,
    response_model_exclude_none=True,
    operation_id="read_allergy",
)
async def read_allergy(request: Request, allergy_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    item = await repo.get_by_id(Allergy, allergy_id)
    if item is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(allergy_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": AllergyDTO.model_validate(item).model_dump(exclude_none=True)},
    )


@router.put(
    "/{allergy_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AllergySingleEnvelope,
    response_model_exclude_none=True,
    operation_id="update_allergy",
)
async def update_allergy(request: Request, allergy_id: UUID, payload: AllergyUpdate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.update_by_id(Allergy, allergy_id, clean_update(payload))
    if obj is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(allergy_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": AllergyDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/{allergy_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AllergyDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_allergy",
)
async def delete_allergy(request: Request, allergy_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    deleted = await repo.delete_by_id(Allergy, allergy_id)
    if not deleted:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(allergy_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=f"Allergy with id {allergy_id} deleted.",
        data={"deleted": True, "id": str(allergy_id)},
    )