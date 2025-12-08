
# # app/api/v1/users/users_routes.py
# from fastapi import APIRouter, Depends
# from app.database.firebase_auth import get_current_user

# router = APIRouter(prefix="/api/v1/auth_firebase", tags=["User_Settings"])

# @router.get("/me")
# def get_me(decoded = Depends(get_current_user)):
#     return {
#         "user_id": decoded.get("uid") or decoded.get("user_id") or decoded.get("sub"),
#         "email": decoded.get("email"),
#         "firebase_claims": decoded,
#     }
