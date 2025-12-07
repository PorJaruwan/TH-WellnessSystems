# auth_controller.py
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr
from app.api.v1.users.auth_service import signup_user, login_user
from app.core.security import decode_supabase_jwt
from gotrue.errors import AuthApiError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


router = APIRouter(
    prefix="/api/v1/auth_supabase",
    tags=["User_Settings"]
)

bearer = HTTPBearer(auto_error=True)

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

def _serialize_auth_response(resp):
    return {
        "user": resp.user.model_dump() if resp.user else None,
        "session": resp.session.model_dump() if resp.session else None,
    }

@router.post("/signup")
def signup(data: AuthRequest):
    try:
        resp = signup_user(data.email, data.password)
        return {"success": True, **_serialize_auth_response(resp)}
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(data: AuthRequest):
    try:
        resp = login_user(data.email, data.password)
        return {
            "success": True,
            "access_token": resp.session.access_token if resp.session else None,
            "refresh_token": resp.session.refresh_token if resp.session else None,
            "user": resp.user.model_dump() if resp.user else None,
        }
    except AuthApiError as e:
        raise HTTPException(status_code=401, detail=str(e))

# @router.get("/me")
# def get_me(authorization: str = Header(...)):
#     token = authorization.replace("Bearer ", "")
#     payload = decode_supabase_jwt(token)
#     return {"user_id": payload["sub"], "email": payload.get("email")}

# @router.get("/me")
# def get_me(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
#     token = credentials.credentials  # ได้เฉพาะตัว token ไม่ต้องตัด "Bearer "
#     try:
#         payload = decode_supabase_jwt(token)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return {"user_id": payload["sub"], "email": payload.get("email")}

@router.get("/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials
    try:
        payload = decode_supabase_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user_id": payload["sub"], "email": payload.get("email")}


# # ✅ auth_controller.py
# from fastapi import APIRouter, Request, Depends, Header
# from pydantic import BaseModel

# from app.api.v1.users.auth_service import signup_user, login_user
# from app.core.security import decode_supabase_jwt

# router = APIRouter(
#     prefix="/api/v1/auth_supabase",
#     tags=["User_Settings"]
# )

# class AuthRequest(BaseModel):
#     email: str
#     password: str

# @router.post("/signup")
# def signup(data: AuthRequest):
#     res = signup_user(data.email, data.password)
#     if res.get("error"):
#         return {"success": False, "error": res.error.message}
#     return {"success": True, "user": res.user}

# @router.post("/login")
# def login(data: AuthRequest):
#     res = login_user(data.email, data.password)
#     if res.get("error"):
#         return {"success": False, "error": res.error.message}
#     return {
#         "success": True,
#         "access_token": res.session.access_token,
#         "refresh_token": res.session.refresh_token,
#         "user": res.user,
#     }

# @router.get("/me")
# def get_me(authorization: str = Header(...)):
#     token = authorization.replace("Bearer ", "")
#     payload = decode_supabase_jwt(token)
#     return {"user_id": payload["sub"], "email": payload["email"]}