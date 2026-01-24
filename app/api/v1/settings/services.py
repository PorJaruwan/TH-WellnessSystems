# app/api/v1/settings/services.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.settings_model import ServiceCreate, ServiceUpdate
from app.api.v1.models.settings_response_model import ServiceResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_service,
    orm_get_all_services,
    orm_get_service_by_id,
    orm_update_service_by_id,
    orm_delete_service_by_id,
)

router = APIRouter(
    prefix="/api/v1/services",
    tags=["Core_Settings"]
)


@router.post(
    "/create",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def create_service_by_id(service: ServiceCreate, session: AsyncSession = Depends(get_db)):
    try:
        cleaned = clean_create(service)  # ✅ replaces local clean_payload

        obj = await orm_create_service(session, cleaned)
        payload = ServiceResponse.model_validate(obj).model_dump(exclude_none=True)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"service": payload},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_services(session: AsyncSession = Depends(get_db)):
    items = await orm_get_all_services(session)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})

    payload = [ServiceResponse.model_validate(x).model_dump(exclude_none=True) for x in items]
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(payload), "services": payload},
    )


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_service_by_id(service_id: UUID, session: AsyncSession = Depends(get_db)):
    obj = await orm_get_service_by_id(session, service_id)
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_id": str(service_id)})

    payload = ServiceResponse.model_validate(obj).model_dump(exclude_none=True)
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"service": payload},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_service_by_id(service_id: UUID, payload: ServiceUpdate, session: AsyncSession = Depends(get_db)):
    obj = await orm_update_service_by_id(session, service_id, clean_update(payload))
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["UPDATED"][1],
        data={"service": ServiceResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_service_by_id(service_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        ok = await orm_delete_service_by_id(session, service_id)
        if not ok:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_id": str(service_id)})

        return ResponseHandler.success(
            message=f"Services with ID {service_id} deleted.",
            data={"service_id": str(service_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
