# app/api/v1/users/auth.py

from __future__ import annotations

from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, Header, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.core.config import get_settings, Settings  # DI


# =========================================================
# TOKEN VERIFY (Supabase JWT) - DI
# =========================================================
def verify_token(
    authorization: Optional[str] = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    DEV:
      - ไม่ require Authorization -> คืน mock claims

    HEADER:
      - ไม่ require Authorization -> คืน mock claims
      - (ใช้ header X-Company-Code / X-Patient-Id เป็นหลัก)

    JWT:
      - require Authorization: Bearer <token>
      - decode ด้วย SUPABASE_JWT_SECRET
    """
    mode = settings.AUTH_MODE.upper()

    if mode in ("DEV", "HEADER"):
        return {"sub": "00000000-0000-0000-0000-000000000000", "email": f"{mode.lower()}@wellplus.local"}

    # JWT mode
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format (expected Bearer)")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty Bearer token")

    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET is not configured")

    aud = getattr(settings, "SUPABASE_JWT_AUD", "authenticated")

    try:
        from jose import jwt  # pip install python-jose

        claims = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience=aud,
            options={"verify_aud": True},
        )
        return claims
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token verification failed: {e}")


def _jwt_user_id(decoded_token: Dict[str, Any], settings: Settings) -> Optional[UUID]:
    if settings.AUTH_MODE.upper() != "JWT":
        return None

    sub = decoded_token.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token missing 'sub'")

    try:
        return UUID(str(sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid 'sub' format")


# =========================================================
# USER PROFILE LOOKUP (for JWT mode)
# =========================================================
async def _load_user_profile(db: AsyncSession, user_id: UUID) -> Dict[str, Any] | None:
    q = text("""
        select
          up.company_code,
          up.patient_id,
          up.staff_id,
          up.actor_type,
          up.email,
          up.is_active
        from public.user_profiles up
        where up.user_id = :user_id
        limit 1
    """)
    row = (await db.execute(q, {"user_id": str(user_id)})).mappings().first()
    return dict(row) if row else None


async def _get_profile_or_401(
    db: AsyncSession,
    decoded_token: Dict[str, Any],
    settings: Settings,
) -> Dict[str, Any]:
    uid = _jwt_user_id(decoded_token, settings)
    if not uid:
        raise HTTPException(status_code=401, detail="Unauthorized")

    profile = await _load_user_profile(db, uid)
    if not profile:
        raise HTTPException(status_code=401, detail="User profile not found")
    if profile.get("is_active") is False:
        raise HTTPException(status_code=403, detail="User is inactive")
    return profile


# =========================================================
# COMPANY CONTEXT
# =========================================================
async def current_company_code(
    db: AsyncSession = Depends(get_db),
    decoded_token: dict = Depends(verify_token),
    settings: Settings = Depends(get_settings),
    x_company_code: str | None = Header(default=None, alias="X-Company-Code"),
) -> str | None:
    """
    DEV:
      - header (ถ้ามี) -> ใช้
      - ไม่มีก็ fallback .env WELLPLUS_COMPANY_CODE

    HEADER (PROD interim):
      - ต้องมี header X-Company-Code เท่านั้น (ไม่ fallback .env)
      - ถ้าไม่มี -> None (router จะตอบ 401 ตามที่คุณทำไว้)

    JWT (PROD):
      - derive จาก user_profiles.company_code
    """
    mode = settings.AUTH_MODE.upper()

    if mode == "DEV":
        return (x_company_code or settings.WELLPLUS_COMPANY_CODE).strip()

    if mode == "HEADER":
        return x_company_code.strip() if x_company_code else None

    # JWT
    profile = await _get_profile_or_401(db, decoded_token, settings)
    return profile.get("company_code")


# =========================================================
# PATIENT CONTEXT
# =========================================================
async def current_patient_id(
    db: AsyncSession = Depends(get_db),
    decoded_token: dict = Depends(verify_token),
    settings: Settings = Depends(get_settings),
    x_patient_id: str | None = Header(default=None, alias="X-Patient-Id"),
) -> str | None:
    """
    DEV:
      - header (ถ้ามี) -> ใช้
      - ไม่มีก็ fallback .env WELLPLUS_DEV_PATIENT_ID

    HEADER (PROD interim):
      - ต้องมี header X-Patient-Id เท่านั้น (ไม่ fallback .env)
      - ถ้าไม่มี -> None (router จะตอบ 403 สำหรับ patient-only)

    JWT (PROD):
      - derive จาก user_profiles.patient_id
    """
    mode = settings.AUTH_MODE.upper()

    if mode == "DEV":
        if x_patient_id:
            return x_patient_id.strip()
        return settings.WELLPLUS_DEV_PATIENT_ID

    if mode == "HEADER":
        return x_patient_id.strip() if x_patient_id else None

    # JWT
    profile = await _get_profile_or_401(db, decoded_token, settings)
    pid = profile.get("patient_id")
    return str(pid) if pid else None



## remark: 2026-02-16 : เพิ่มให้สามารถใส่ Header ที่ Prod ได้
# # app/api/v1/users/auth.py

# from __future__ import annotations

# from typing import Optional, Dict, Any
# from uuid import UUID

# from fastapi import HTTPException, Header, Depends, status
# from sqlalchemy import text
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.database.session import get_db
# from app.core.config import get_settings, Settings  # ✅ DI settings


# # =========================================================
# # TOKEN VERIFY (Supabase JWT) - DI
# # =========================================================
# def verify_token(
#     authorization: Optional[str] = Header(default=None),
#     settings: Settings = Depends(get_settings),
# ) -> Dict[str, Any]:
#     """
#     DEV:
#       - ไม่ require Authorization -> คืน mock claims
#     JWT (PROD):
#       - require Authorization: Bearer <token>
#       - decode ด้วย settings.SUPABASE_JWT_SECRET
#     """
#     auth_mode = settings.AUTH_MODE.upper()

#     if auth_mode == "DEV":
#         # mock user id (uuid-like) เพื่อไม่ให้ code downstream พัง
#         return {"sub": "00000000-0000-0000-0000-000000000000", "email": "dev@wellplus.local"}

#     # JWT mode
#     if not authorization:
#         raise HTTPException(status_code=401, detail="Missing Authorization header")
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid token format (expected Bearer)")

#     token = authorization.split(" ", 1)[1].strip()
#     if not token:
#         raise HTTPException(status_code=401, detail="Empty Bearer token")

#     if not settings.SUPABASE_JWT_SECRET:
#         raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET is not configured")

#     # Supabase access token ปกติ aud = "authenticated"
#     aud = getattr(settings, "SUPABASE_JWT_AUD", "authenticated")

#     try:
#         from jose import jwt  # pip install python-jose

#         claims = jwt.decode(
#             token,
#             settings.SUPABASE_JWT_SECRET,
#             algorithms=["HS256"],
#             audience=aud,
#             options={"verify_aud": True},
#         )
#         return claims
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Token verification failed: {e}",
#         )


# def _jwt_user_id(decoded_token: Dict[str, Any], settings: Settings) -> Optional[UUID]:
#     """
#     Supabase JWT: 'sub' == auth.users.id (UUID)
#     DEV: return None (ใช้ header fallback)
#     """
#     if settings.AUTH_MODE.upper() == "DEV":
#         return None

#     sub = decoded_token.get("sub")
#     if not sub:
#         raise HTTPException(status_code=401, detail="Token missing 'sub'")

#     try:
#         return UUID(str(sub))
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid 'sub' format")


# # =========================================================
# # USER PROFILE LOOKUP (เป๊ะตาม schema ที่คุณส่ง)
# # public.user_profiles.user_id FK -> auth.users.id
# # columns: company_code, patient_id, staff_id, actor_type, email, is_active
# # =========================================================
# async def _load_user_profile(db: AsyncSession, user_id: UUID) -> Dict[str, Any] | None:
#     q = text("""
#         select
#           up.company_code,
#           up.patient_id,
#           up.staff_id,
#           up.actor_type,
#           up.email,
#           up.is_active
#         from public.user_profiles up
#         where up.user_id = :user_id
#         limit 1
#     """)
#     row = (await db.execute(q, {"user_id": str(user_id)})).mappings().first()
#     return dict(row) if row else None


# async def _get_profile_or_401(
#     db: AsyncSession,
#     decoded_token: Dict[str, Any],
#     settings: Settings,
# ) -> Dict[str, Any]:
#     uid = _jwt_user_id(decoded_token, settings)
#     if not uid:
#         raise HTTPException(status_code=401, detail="Unauthorized")

#     profile = await _load_user_profile(db, uid)
#     if not profile:
#         raise HTTPException(status_code=401, detail="User profile not found")

#     if profile.get("is_active") is False:
#         raise HTTPException(status_code=403, detail="User is inactive")

#     return profile


# # =========================================================
# # COMPANY CONTEXT
# # =========================================================
# async def current_company_code(
#     db: AsyncSession = Depends(get_db),
#     decoded_token: dict = Depends(verify_token),
#     settings: Settings = Depends(get_settings),
#     x_company_code: str | None = Header(default=None, alias="X-Company-Code"),
# ) -> str | None:
#     """
#     DEV:
#       - ใช้ X-Company-Code ถ้ามี ไม่มีก็ settings.WELLPLUS_COMPANY_CODE
#     JWT (PROD):
#       - ใช้ profile.company_code จาก user_profiles
#     """
#     if settings.AUTH_MODE.upper() == "DEV":
#         return (x_company_code or settings.WELLPLUS_COMPANY_CODE).strip()

#     profile = await _get_profile_or_401(db, decoded_token, settings)
#     return profile.get("company_code")


# # =========================================================
# # PATIENT CONTEXT (Required for patient-only endpoints)
# # =========================================================
# async def current_patient_id(
#     db: AsyncSession = Depends(get_db),
#     decoded_token: dict = Depends(verify_token),
#     settings: Settings = Depends(get_settings),
#     x_patient_id: str | None = Header(default=None, alias="X-Patient-Id"),
# ) -> str | None:
#     """
#     DEV:
#       - ใช้ X-Patient-Id ถ้ามี
#       - ไม่มีก็ settings.WELLPLUS_DEV_PATIENT_ID (ถ้าตั้ง)
#     JWT (PROD):
#       - profile.patient_id (ถ้าเป็น staff login จะ None -> router ตอบ 403)
#     """
#     if settings.AUTH_MODE.upper() == "DEV":
#         if x_patient_id:
#             return x_patient_id.strip()
#         return settings.WELLPLUS_DEV_PATIENT_ID

#     profile = await _get_profile_or_401(db, decoded_token, settings)
#     pid = profile.get("patient_id")
#     return str(pid) if pid else None


# # =========================================================
# # (Optional) STAFF CONTEXT (เผื่อ staff-only endpoints)
# # =========================================================
# async def current_staff_id(
#     db: AsyncSession = Depends(get_db),
#     decoded_token: dict = Depends(verify_token),
#     settings: Settings = Depends(get_settings),
#     x_staff_id: str | None = Header(default=None, alias="X-Staff-Id"),
# ) -> str | None:
#     if settings.AUTH_MODE.upper() == "DEV":
#         if x_staff_id:
#             return x_staff_id.strip()
#         # optional: ถ้าคุณจะเพิ่ม WELLPLUS_DEV_STAFF_ID ใน Settings ค่อยใช้
#         return getattr(settings, "WELLPLUS_DEV_STAFF_ID", None)

#     profile = await _get_profile_or_401(db, decoded_token, settings)
#     sid = profile.get("staff_id")
#     return str(sid) if sid else None
