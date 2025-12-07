# app/api/v1/settings/room_availabilities.py

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.settings_model import RoomAvailabilitiesCreateModel, RoomAvailabilitiesUpdateModel
from app.api.v1.services.settings_service import (
    post_room_availability,
    get_all_room_availability,
    get_room_availability_by_id,
    put_room_availability_by_id,
    delete_room_availability_by_id,
)

router = APIRouter(
    prefix="/api/v1/room_availabilities",
    tags=["Room_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_room_availability(room_availabilities: RoomAvailabilitiesCreateModel):
    try:
        data = jsonable_encoder(room_availabilities)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = post_room_availability(cleaned_data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed.")
        return ResponseHandler.success(ResponseCode.SUCCESS["REGISTERED"][1], data={"room_availabilities": res.data[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_room_availabilities():
    res = get_all_room_availability()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "room_availabilities": res.data})


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_room_availability(room_availability_id: UUID):
    res = get_room_availability_by_id(room_availability_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_availability_id": str(room_availability_id)})
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"room_availabilities": res.data[0]})


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_room_availability(room_availability_id: UUID, room_availabilities: RoomAvailabilitiesUpdateModel):
    updated = jsonable_encoder(room_availabilities)
    res = put_room_availability_by_id(room_availability_id, updated)

    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_availability_id": str(room_availability_id)})

    return ResponseHandler.success(ResponseCode.SUCCESS["UPDATED"][1], data={"room_availabilities": res.data[0]})


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_room_availability(room_availability_id: UUID):
    res = delete_room_availability_by_id(room_availability_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_availability_id": str(room_availability_id)})
    return ResponseHandler.success(f"Deleted successfully.", data={"room_availability_id": str(room_availability_id)})



# @router.post("/create-by-id/", response_class=UnicodeJSONResponse)
# def create_room_availability_by_id(room_availabilities: RoomAvailabilitiesCreateModel):
#     try:
#         data = jsonable_encoder(room_availabilities)
#         cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
#         res = insert_room_availability(cleaned_data)
#         if not res.data:
#             raise HTTPException(status_code=400, detail="Insert failed.")
#         return ResponseHandler.success(ResponseCode.SUCCESS["REGISTERED"][1], data={"room_availabilities": res.data[0]})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/search-by-all/", response_class=UnicodeJSONResponse)
# def read_room_availability_by_all():
#     res = get_all_room_availabilities()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])
#     return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "room_availabilities": res.data})

# @router.get("/search-by-id/", response_class=UnicodeJSONResponse)
# def read_room_availability_by_id(room_availability_id: UUID):
#     res = get_room_availability_by_id(room_availability_id)
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_availability_id": str(room_availability_id)})
#     return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"room_availabilities": res.data[0]})

# @router.put("/update-by-id/", response_class=UnicodeJSONResponse)
# def update_room_availability_by_id(room_availability_id: UUID, room_availabilities: RoomAvailabilitiesUpdateModel):
#     updated = room_availabilities.dict()
#     res = update_room_availability_by_id(room_availability_id, updated)
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_availability_id": str(room_availability_id)})
#     return ResponseHandler.success(ResponseCode.SUCCESS["UPDATED"][1], data={"room_availabilities": res.data[0]})

# @router.delete("/delete-by-id/", response_class=UnicodeJSONResponse)
# def delete_room_availability_by_id(room_availability_id: UUID):
#     res = delete_room_availability_by_id(room_availability_id)
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_availability_id": str(room_availability_id)})
#     return ResponseHandler.success(f"Deleted successfully.", data={"room_availability_id": str(room_availability_id)})
