# app/api/v1/settings/departments.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.database.session import get_db
from app.api.v1.models.settings_model import DepartmentCreate, DepartmentUpdate
from app.api.v1.models.settings_response_model import DepartmentResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_department,
    orm_get_all_departments,
    orm_get_department_by_id,
    orm_update_department_by_id,
    orm_delete_department_by_id,
)

router = APIRouter(
    prefix="/api/v1/departments", 
    tags=["Core_Settings"])



@router.post("/create", response_class=UnicodeJSONResponse)
async def create_department(payload: DepartmentCreate, session: AsyncSession = Depends(get_db)):
    obj = await orm_create_department(session, clean_create(payload))
    return ResponseHandler.success(
        ResponseCode.SUCCESS["REGISTERED"][1],
        data={"department": DepartmentResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_departments(session: AsyncSession = Depends(get_db)):
    items = await orm_get_all_departments(session)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})

    out = [DepartmentResponse.model_validate(x).model_dump(exclude_none=True) for x in items]
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(out), "departments": out},
    )


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_department_id(department_id: UUID, session: AsyncSession = Depends(get_db)):
    obj = await orm_get_department_by_id(session, department_id)
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"department_id": str(department_id)})

    out = DepartmentResponse.model_validate(obj).model_dump(exclude_none=True)
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"department": out})


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_department_id(departmentId: UUID, payload: DepartmentUpdate, session: AsyncSession = Depends(get_db)):
    obj = await orm_update_department_by_id(session, departmentId, clean_update(payload))
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["UPDATED"][1],
        data={"department": DepartmentResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_department(departmentId: UUID, session: AsyncSession = Depends(get_db)):
    ok = await orm_delete_department_by_id(session, departmentId)
    if not ok:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"departmentId": str(departmentId)})

    return ResponseHandler.success(
        message=f"Department with ID {departmentId} deleted.",
        data={"department_Id": str(departmentId)},
    )
