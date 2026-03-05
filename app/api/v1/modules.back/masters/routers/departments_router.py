from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import DepartmentCreate, DepartmentUpdate
from app.api.v1.modules.masters.models._envelopes import DepartmentCreateEnvelope, DepartmentUpdateEnvelope, DepartmentDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import DepartmentResponse

from app.api.v1.modules.masters.repositories.departments_crud_repository import DepartmentCrudRepository
from app.api.v1.modules.masters.services.departments_crud_service import DepartmentCrudService

router = APIRouter()
# router = APIRouter(prefix="/departments", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> DepartmentCrudService:
    return DepartmentCrudService(session=session, repo=DepartmentCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_departments(
    request: Request,
    payload: DepartmentCreate,
    svc: DepartmentCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = DepartmentResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_departments(
    request: Request,
    department_id: UUID,
    payload: DepartmentUpdate,
    svc: DepartmentCrudService = Depends(get_crud_service),
):
    obj = await svc.update(department_id, payload.model_dump(exclude_none=True))
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
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=DepartmentDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_departments(
    request: Request,
    department_id: UUID,
    svc: DepartmentCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(department_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"department_id": str(department_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "department_id": str(department_id)},
    )
