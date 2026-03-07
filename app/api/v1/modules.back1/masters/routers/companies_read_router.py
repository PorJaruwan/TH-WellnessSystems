from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.companies_read_repository import CompanyReadRepository
from app.api.v1.modules.masters.services.companies_read_service import CompanyReadService
from app.api.v1.modules.masters.models._envelopes import CompanyGetEnvelope
from app.api.v1.modules.masters.models.dtos import CompanyResponse

router = APIRouter()
# router = APIRouter(prefix="/companies", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> CompanyReadService:
    return CompanyReadService(CompanyReadRepository(session))


@router.get(
    "/{company_code}",
    response_class=UnicodeJSONResponse,
    response_model=CompanyGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_companies_by_id",
)
async def read_companies_by_id(
    request: Request,
    company_code: str,
    svc: CompanyReadService = Depends(get_read_service),
):
    obj = await svc.get(company_code)
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
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": item},
    )
