
# app/api/v1/users/users_routes.py
from fastapi import APIRouter, Depends
from app.database.firebase_auth import get_current_user



router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/auth_firebase",
    tags=["User_Authen"],
)

@router.get("/me")
def get_me(decoded = Depends(get_current_user)):
    return {
        "user_id": decoded.get("uid") or decoded.get("user_id") or decoded.get("sub"),
        "email": decoded.get("email"),
        "firebase_claims": decoded,
    }
