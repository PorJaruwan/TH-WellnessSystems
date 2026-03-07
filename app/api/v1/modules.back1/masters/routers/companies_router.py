from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import CompanyCreate, CompanyUpdate
from app.api.v1.modules.masters.models._envelopes import CompanyCreateEnvelope, CompanyUpdateEnvelope, CompanyDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import CompanyResponse

from app.api.v1.modules.masters.repositories.companies_crud_repository import CompanyCrudRepository
from app.api.v1.modules.masters.services.companies_crud_service import CompanyCrudService

router = APIRouter()
# router = APIRouter(prefix="/companies", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> CompanyCrudService:
    return CompanyCrudService(session=session, repo=CompanyCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=CompanyCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_companies",
)
async def create_companies(
    request: Request,
    payload: CompanyCreate,
    svc: CompanyCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = CompanyResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{company_code}",
    response_class=UnicodeJSONResponse,
    response_model=CompanyUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_companies",
)
async def update_companies(
    request: Request,
    company_code: str,
    payload: CompanyUpdate,
    svc: CompanyCrudService = Depends(get_crud_service),
):
    obj = await svc.update(company_code, payload.model_dump(exclude_none=True))
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"company_code": str(company_code)},
            status_code=404,
        )
    item = CompanyResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{company_code}",
    response_class=UnicodeJSONResponse,
    response_model=CompanyDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_companies",
)
async def delete_companies(
    request: Request,
    company_code: str,
    svc: CompanyCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(company_code)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"company_code": str(company_code)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "company_code": str(company_code)},
    )
