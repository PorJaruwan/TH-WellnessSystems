# app/api/v1/patients/sale_staff.py

from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.patients.models.schemas import SaleStaffCreate, SaleStaffUpdate
from app.api.v1.modules.patients.models.dtos import SaleStaffDTO
from app.api.v1.modules.patients.models._envelopes.sale_staff_envelopes import (
    SaleStaffSingleEnvelope,
    SaleStaffListEnvelope,
    SaleStaffDeleteEnvelope,
)

from app.api.v1.modules.patients.repositories.masterdata_repository import MasterDataRepository
from app.api.v1.modules.patients.services.masterdata_service import MasterDataService
from app.db.models.patient_settings import SaleStaff


router = APIRouter()

DEFAULT_SORT_BY = "sale_person_name"
ALLOWED_SORT_FIELDS = ["sale_person_name", "department_name", "created_at", "updated_at", "is_active"]
SEARCH_FIELDS = ["sale_person_name", "department_name"]


def get_masterdata_service(db: AsyncSession = Depends(get_db)) -> MasterDataService:
    return MasterDataService(MasterDataRepository(db))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="create_sale_staff",
)
async def create_sale_staff(request: Request, payload: SaleStaffCreate, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    obj = await repo.create(SaleStaff, payload.model_dump())
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": SaleStaffDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffListEnvelope,
    response_model_exclude_none=True,
    operation_id="search_sale_staff",
)
async def search_sale_staff(
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
        model=SaleStaff,
        dto=SaleStaffDTO,
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
    "/{sale_staff_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="read_sale_staff",
)
async def read_sale_staff(request: Request, sale_staff_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    item = await repo.get_by_id(SaleStaff, sale_staff_id)
    if item is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(sale_staff_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": SaleStaffDTO.model_validate(item).model_dump(exclude_none=True)},
    )


@router.put(
    "/{sale_staff_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffSingleEnvelope,
    response_model_exclude_none=True,
    operation_id="update_sale_staff",
)
async def update_sale_staff(
    request: Request, sale_staff_id: UUID, payload: SaleStaffUpdate, db: AsyncSession = Depends(get_db)
):
    repo = MasterDataRepository(db)
    obj = await repo.update_by_id(SaleStaff, sale_staff_id, payload.model_dump(exclude_unset=True))
    if obj is None:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(sale_staff_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": SaleStaffDTO.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/{sale_staff_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_sale_staff",
)
async def delete_sale_staff(request: Request, sale_staff_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = MasterDataRepository(db)
    deleted = await repo.delete_by_id(SaleStaff, sale_staff_id)
    if not deleted:
        return ResponseHandler.error_from_request(
            request, *("DATA_404", "Resource not found."), details={"id": str(sale_staff_id)}
        )
    return ResponseHandler.success_from_request(
        request,
        message=f"SaleStaff with id {sale_staff_id} deleted.",
        data={"deleted": True, "id": str(sale_staff_id)},
    )