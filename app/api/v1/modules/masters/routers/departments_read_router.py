from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.departments_read_repository import DepartmentReadRepository
from app.api.v1.modules.masters.services.departments_read_service import DepartmentReadService
from app.api.v1.modules.masters.models._envelopes import DepartmentGetEnvelope
from app.api.v1.modules.masters.models.dtos import DepartmentResponse

router = APIRouter()
# router = APIRouter(prefix="/departments", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> DepartmentReadService:
    return DepartmentReadService(DepartmentReadRepository(session))


@router.get(
    "/{department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentGetEnvelope,
    response_model_exclude_none=True,
)
async def read_departments_by_id(
    request: Request,
    department_id: UUID,
    svc: DepartmentReadService = Depends(get_read_service),
):
    obj = await svc.get(department_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"department_id": str(department_id)},
            status_code=404,
        )
    item = DepartmentResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": item},
    )
