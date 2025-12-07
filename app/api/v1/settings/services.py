from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.settings_model import ServicesCreateModel, ServicesUpdateModel
from app.api.v1.services.settings_service import (
    post_service,
    get_all_services,
    get_service_by_id,
    put_service_by_id,
    delete_service_by_id,
    generate_service_update_payload,
    format_service_results
)
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

router = APIRouter(
    prefix="/api/v1/services",
    tags=["Service_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_service_by_id(service: ServicesCreateModel):
    try:
        data = jsonable_encoder(service)
        res = post_service(data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data=jsonable_encoder({"services": res.data[0]})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_service_by_all():
    res = get_all_services()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    result_list = format_service_results(res.data)
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=jsonable_encoder({"total": len(result_list), "services": result_list})
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_service_by_id(service_id: UUID):
    res = get_service_by_id(service_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_id": str(service_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=jsonable_encoder({"services": res.data[0]})
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_service_by_id(service_id: UUID, service: ServicesUpdateModel):
    updated = generate_service_update_payload(service)
    res = put_service_by_id(service_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_id": str(service_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data=jsonable_encoder({"services": res.data[0]})
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_service_by_id(service_id: UUID):
    try:
        res = delete_service_by_id(service_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_id": str(service_id)})
        return ResponseHandler.success(
            message=f"Services with ID {service_id} deleted.",
            data=jsonable_encoder({"service_id": str(service_id)})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))