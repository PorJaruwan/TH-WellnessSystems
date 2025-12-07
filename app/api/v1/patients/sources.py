# app/api/v1/settings/source.py
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from uuid import UUID
from app.api.v1.models.patients_model import SourcesCreateModel, SourcesUpdateModel
from app.api.v1.services.patients_service import (
    post_source_service,
    get_all_source_service,
    get_source_by_id_service,
    put_source_by_id_service,
    delete_source_by_id_service,
    generate_source_update_payload,
    format_source_results
)
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

router = APIRouter(
    prefix="/api/v1/sources",
    tags=["Patient_Settings"]
)

# ✅ CREATE
@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_source_by_id(sources: SourcesCreateModel):
    try:
        data = jsonable_encoder(sources)
        res = post_source_service(data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"sources": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ READ ALL
@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_source_by_all():
    res = get_all_source_service()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})

    result_list = format_source_results(res.data)

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(result_list), "sources": result_list}
    )

# ✅ READ BY ID
@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_source_by_id(source_id: UUID):
    res = get_source_by_id_service(source_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"source_id": str(source_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"sources": res.data[0]}
    )

# ✅ UPDATE
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_source_by_id(source_id: UUID, sourc: SourcesUpdateModel):
    updated = generate_source_update_payload(sourc)
    res = put_source_by_id_service(source_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"source_id": str(source_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"sources": res.data[0]}
    )

# ✅ DELETE
@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_source_by_id(source_id: UUID):
    try:
        res = delete_source_by_id_service(source_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"source_id": str(source_id)})
        return ResponseHandler.success(
            message=f"source with ID {source_id} deleted.",
            data={"source_id": str(source_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))