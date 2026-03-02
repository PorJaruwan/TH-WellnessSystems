# app/api/v1/users/auth.py

from __future__ import annotations

from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, Header, Query, Depends, status

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
    # 👇 รับจาก query param ก่อน
    company_code: str | None = Query(default=None, alias="company_code"),
    # 👇 ยังรองรับ header ได้
    x_company_code: str | None = Header(default=None, alias="X-Company-Code"),
) -> str | None:
    mode = settings.AUTH_MODE.upper()

    if mode == "DEV":
        return (company_code or x_company_code or settings.WELLPLUS_COMPANY_CODE).strip()

    if mode == "HEADER":
        value = company_code or x_company_code
        return value.strip() if value else None

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
    # 👇 รับจาก query param ก่อน
    patient_id: str | None = Query(default=None, alias="patient_id"),
    # 👇 ยังรองรับ header ได้
    x_patient_id: str | None = Header(default=None, alias="X-Patient-Id"),
) -> str | None:
    mode = settings.AUTH_MODE.upper()

    if mode == "DEV":
        if patient_id:
            return patient_id.strip()
        if x_patient_id:
            return x_patient_id.strip()
        return settings.WELLPLUS_DEV_PATIENT_ID

    if mode == "HEADER":
        value = patient_id or x_patient_id
        return value.strip() if value else None

    # JWT
    profile = await _get_profile_or_401(db, decoded_token, settings)
    pid = profile.get("patient_id")
    return str(pid) if pid else None

