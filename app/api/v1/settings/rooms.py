# app/api/v1/settings/rooms.py
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.settings_model import RoomsCreateModel, RoomsUpdateModel
from app.api.v1.services.settings_service import (
    post_room,
    get_all_rooms,
    get_room_by_id,
    put_room_by_id,
    delete_room_by_id
)

router = APIRouter(
    prefix="/api/v1/rooms",
    tags=["Room_Settings"]
)

# ✅ CREATE
@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_room(rooms: RoomsCreateModel):
    try:
        data = jsonable_encoder(rooms)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = post_room(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"rooms": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ READ ALL
@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_rooms():
    res = get_all_rooms()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "rooms": res.data}
    )

# ✅ READ BY ID
@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_room(room_id: UUID):
    res = get_room_by_id(room_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_id": str(room_id)})

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"rooms": res.data[0]}
    )

# ✅ UPDATE
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_room(room_id: UUID, rooms: RoomsUpdateModel):
    updated = jsonable_encoder(rooms)  # ✅ ป้องกัน datetime error
    res = put_room_by_id(room_id, updated)

    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_id": str(room_id)})

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"rooms": res.data[0]}
    )    

# ✅ DELETE
@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_room(room_id: UUID):
    res = delete_room_by_id(room_id)

    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_id": str(room_id)})

    return ResponseHandler.success(
        message=f"Room with room_id: {room_id} deleted.",
        data={"room_id": str(room_id)}
    )
