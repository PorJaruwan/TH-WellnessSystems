# app/api/v1/settings/service_types.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import ServiceTypeCreate, ServiceTypeUpdate
from app.api.v1.models.settings_response_model import ServiceTypeResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_service_type,
    orm_get_all_service_types,
    orm_get_service_type_by_id,
    orm_update_service_type_by_id,
    orm_delete_service_type_by_id,
)

router = APIRouter(
    prefix="/api/v1/service_types",
    tags=["Core_Settings"]
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_service_type(payload: ServiceTypeCreate, session: AsyncSession = Depends(get_db)):
    obj = await orm_create_service_type(session, clean_create(payload))
    return ResponseHandler.success(
        ResponseCode.SUCCESS["REGISTERED"][1],
        data={"service_type": ServiceTypeResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_service_type_by_all(session: AsyncSession = Depends(get_db)):
    items = await orm_get_all_service_types(session)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})

    payload = [ServiceTypeResponse.model_validate(x).model_dump(exclude_none=True) for x in items]
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(payload), "service_types": payload},
    )


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_service_type_by_id(service_type_id: UUID, session: AsyncSession = Depends(get_db)):
    obj = await orm_get_service_type_by_id(session, service_type_id)
    if not obj:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"service_type_id": str(service_type_id)},
        )

    payload = ServiceTypeResponse.model_validate(obj).model_dump(exclude_none=True)
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"service_type": payload})


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_service_type(service_type_id: UUID, payload: ServiceTypeUpdate, session: AsyncSession = Depends(get_db)):
    obj = await orm_update_service_type_by_id(session, service_type_id, clean_update(payload))
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["UPDATED"][1],
        data={"service_type": ServiceTypeResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_service_type(service_type_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        ok = await orm_delete_service_type_by_id(session, service_type_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"service_type_id": str(service_type_id)},
            )

        return ResponseHandler.success(
            message=f"service types with service_type_id: {service_type_id} deleted.",
            data={"service_type_id": str(service_type_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
