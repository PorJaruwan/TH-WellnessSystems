from jose import jwt, JWTError
# import requests
from app.core.config import get_settings

settings = get_settings()
# SUPABASE_URL = settings.SUPABASE_URL
# SUPABASE_JWT_PUBLIC_KEY_URL = f"{SUPABASE_URL}/auth/v1/keys"

# โหลด public keys จาก Supabase
# def get_jwt_public_keys():
#     resp = requests.get(SUPABASE_JWT_PUBLIC_KEY_URL)
#     resp.raise_for_status()
#     return resp.json().get("keys", [])

ALGORITHM = "HS256"
JWT_SECRET = settings.SUPABASE_JWT_SECRET  # ต้องเป็น "JWT secret" จากหน้า Auth → JWT ของ Supabase

def decode_supabase_jwt(token: str) -> dict:
    """
    ถอดรหัสและยืนยัน Supabase access_token (HS256)
    - ตรวจ exp อัตโนมัติ
    - ตรวจ aud = "authenticated"
    """
    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM],
            audience="authenticated",          # aud ใน token ของ Supabase คือ "authenticated"
        )
    except JWTError as e:
        # แจง error จริงใน log ของคุณก็ได้ แต่ response ควรเป็น 401
        raise e


# def decode_supabase_jwt(token: str):
#     """
#     ตรวจสอบและถอดรหัส Supabase JWT ด้วย public keys
#     """
#     keys = get_jwt_public_keys()

#     # ลองถอดรหัสด้วยทุก key ที่ได้มา
#     for key in keys:
#         try:
#             return jwt.decode(
#                 token,
#                 key,
#                 algorithms=[key.get("alg", "RS256")],
#                 audience="authenticated",  # ค่า aud ปกติที่ Supabase ใช้
#                 options={"verify_aud": False},  # ถ้าคุณไม่อยากตรวจ aud
#             )
#         except Exception:
#             continue

#     raise ValueError("JWT verification failed")

