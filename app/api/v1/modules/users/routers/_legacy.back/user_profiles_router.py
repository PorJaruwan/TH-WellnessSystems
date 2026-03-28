# app/api/v1/users/user_profiles.py
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.users.models.users_model import UserProfilesCreateModel, UserProfilesUpdateModel, UserProfilesResponseModel
from app.api.v1.modules.users.services.users_service import (
    post_user_profiles, get_all_user_profiles, get_user_profiles_by_id,
    search_user_profiles_by_name,
    transform_user_profiles_with_fullname,  # ✅ นำเข้าใหม่
    put_user_profiles_by_id, delete_user_profiles_by_id, 
)

# logging
from app.core.logging_config import get_service_logger
logger = get_service_logger("service.user_profiles")


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/user_profiles",
    tags=["User_Settings"],
)


# ✅ READ ALL
@router.get("/search", response_class=UnicodeJSONResponse)
def read_all_user_profiles():
    logger.info("📥 [GET] Read all user_profiles")
    res = get_all_user_profiles()

    if not res.data:
        logger.warning("⚠️ No user profile found")
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
    logger.info(f"✅ Retrieved {len(res.data)} user_profiles")
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["LISTED"][1],
        data={"total": len(res.data), "user_profiles": res.data}
    )

# ✅ READ BY ID
@router.get("/{user_profile_id:uuid}", response_class=UnicodeJSONResponse)
def read_user_profile_by_id(user_profile_id: UUID):
    res = get_user_profiles_by_id(str(user_profile_id))  # ✅ เรียก function พร้อมใส่ค่า

    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
            "user_profile_id": str(user_profile_id)
        })

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"user_profiles": res.data[0]}
    )

# ✅ READ BY NAME (refactored)
@router.get("/search-by-name", response_class=UnicodeJSONResponse)
def read_users_by_name(full_name: str = ""):
    res = search_user_profiles_by_name(full_name)

    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"full_name": full_name})

    user_with_fullname = transform_user_profiles_with_fullname(res.data)

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["LISTED"][1],
        data={"total": len(user_with_fullname), "user_profiles": user_with_fullname}
    )


# ✅ CREATE
@router.post("", response_class=UnicodeJSONResponse)
def create_user_profile(user_profiles: UserProfilesCreateModel):
    try:
        data = jsonable_encoder(user_profiles)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = post_user_profiles(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["CREATED"][1],
            data={"user_profiles": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ UPDATE
@router.put("/{user_profile_id:uuid}", response_class=UnicodeJSONResponse)
def update_user_profile(user_profile_id: UUID, user_profiles: UserProfilesUpdateModel):
    updated = jsonable_encoder(user_profiles)  # ✅ ป้องกัน datetime error
    res = put_user_profiles_by_id(user_profile_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_profile_id": str(user_profile_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"user_profiles": res.data[0]}
    )    

# ✅ DELETE
@router.delete("/{user_profile_id:uuid}", response_class=UnicodeJSONResponse)
def delete_user_profile(user_profile_id: UUID):
    res = delete_user_profiles_by_id(user_profile_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_profile_id": str(user_profile_id)})
    return ResponseHandler.success(
        message=f"User profile with id: {user_profile_id} deleted.",
        data={"user_profile_id": str(user_profile_id)}
    )



# # ✅ patch
# @router.patch("/patch-by-me")
# async def update_my_profile(data: ProfileUpdate, request: Request):
#     user = request.scope.get("user")
#     if not user or not user.get("sub"):
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     user_id = user["sub"]

#     res = supabase.table("user_profiles").update(data.dict(exclude_none=True)).eq("id", user_id).execute()
#     if res.error:
#         raise HTTPException(status_code=400, detail=res.error.message)
#     return res.data

# # ✅ webhook
# @router.post("/post-by-new-user")
# async def handle_new_user(payload: dict):
#     user_id = payload.get("id")
#     full_name = payload.get("user_metadata", {}).get("full_name", "Guest")

#     res = supabase.table("user_profiles").insert({
#         "id": user_id,
#         "full_name": full_name
#     }).execute()

#     if res.error:
#         raise HTTPException(status_code=400, detail=res.error.message)
#     return {"status": "ok"}