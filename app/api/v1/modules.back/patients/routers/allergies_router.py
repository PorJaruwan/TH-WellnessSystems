# app/api/v1/patients/allergies.py

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.patients.models.patients_model import AllergyCreate, AllergyUpdate
from app.api.v1.modules.patients.models._envelopes.allergies_envelopes import (
    AllergySingleEnvelope,
    AllergyListEnvelope,
    AllergyDeleteEnvelope,
)
from app.api.v1.modules.patients.models.patient_masterdata_model import AllergyDTO
from app.api.v1.modules.patients.repositories.masterdata_repository import MasterDataRepository
from app.api.v1.modules.patients.services.masterdata_service import MasterDataService

from app.db.models.patient_settings import Allergy

from app.utils.payload_cleaner import clean_create, clean_update
 


def get_masterdata_service(db: AsyncSession = Depends(get_db)) -> MasterDataService:
    """✅ Standard dependency: router -> service -> repo."""
    return MasterDataService(MasterDataRepository(db))

router = APIRouter()


DEFAULT_SORT_BY = "allergy_name"
ALLOWED_SORT_FIELDS = ["allergy_name", "allergy_type", "description", "created_at", "updated_at", "is_active"]


def _get_sort_value(x, field: str) -> str:
    v = x.get(field) if isinstance(x, dict) else getattr(x, field, None)
    return "" if v is None else str(v).lower()


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=AllergySingleEnvelope,
    response_model_exclude_none=True,
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
)
async def search_allergies(
    request: Request,
    svc: MasterDataService = Depends(get_masterdata_service),
    q: Optional[str] = Query(default=None, description="search in allergy_name/description"),
    is_active: Optional[bool] = Query(default=None, description="filter is_active (None=all)"),
    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="asc|desc"),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    filters_payload = {"q": q, "is_active": is_active}

    payload, total, _effective_sort_by = await svc.search_list_payload(
        model=Allergy,
        dto=AllergyDTO,
        q=q,
        is_active=is_active,
        search_fields=["allergy_name", "description"],
        extra_eq_filters=None,
        sort_by=sort_by,
        sort_order=sort_order,
        allowed_sort_fields=ALLOWED_SORT_FIELDS,
        default_sort_by=DEFAULT_SORT_BY,
        limit=limit,
        offset=offset,
        filters_payload=filters_payload,
    )

    if total == 0:
        return ResponseHandler.error_from_request(
            request,
            *("DATA_204", "No data found."),
            details={"filters": filters_payload},
            status_code=404,
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
)
async def read_allergy(request: Request, allergy_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    item = await repo.get_by_id(Allergy, allergy_id)
    if item is None:
        return ResponseHandler.error_from_request(request, *("DATA_404", "Resource not found."), details={"allergy_id": str(allergy_id)})
    return ResponseHandler.success_from_request(request, 
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": AllergyDTO.model_validate(item).model_dump(exclude_none=True)},
    )


@router.put(
    "/{allergy_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AllergySingleEnvelope,
    response_model_exclude_none=True,
)
async def update_allergy(request: Request, allergy_id: UUID, payload: AllergyUpdate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.update_by_id(Allergy, allergy_id, clean_update(payload))
    if obj is None:
        return ResponseHandler.error_from_request(request, *("DATA_404", "Resource not found."), details={"allergy_id": str(allergy_id)})
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
)
async def delete_allergy(request: Request, allergy_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    deleted = await repo.delete_by_id(Allergy, allergy_id)
    if not deleted:
        return ResponseHandler.error_from_request(request, *("DATA_404", "Resource not found."), details={"allergy_id": str(allergy_id)})
    return ResponseHandler.success_from_request(
        request,
        message=f"Allergy with id {allergy_id} deleted.",
        data={"allergy_id": str(allergy_id)},
    )
