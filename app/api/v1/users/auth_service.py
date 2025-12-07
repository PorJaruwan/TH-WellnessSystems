# auth_service.py
from supabase import create_client, Client
import os
from gotrue.types import AuthResponse
from gotrue.errors import AuthApiError

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # ใช้ ANON หรือ SERVICE_ROLE ตาม use case
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def signup_user(email: str, password: str) -> AuthResponse:
    return supabase.auth.sign_up({"email": email, "password": password})

def login_user(email: str, password: str) -> AuthResponse:
    return supabase.auth.sign_in_with_password({"email": email, "password": password})




# # 📦 Supabase Auth Template (Signup, Login, Token Verify)
# # Structure:
# # - auth_service.py → Supabase Auth SDK calls
# # - security.py → JWT verify using Supabase public key
# # - auth_controller.py → FastAPI routes for signup, login, and /me

# # ✅ auth_service.py
# from supabase import create_client, Client
# import os

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# #SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# def signup_user(email: str, password: str):
#     return supabase.auth.sign_up({"email": email, "password": password})

# def login_user(email: str, password: str):
#     return supabase.auth.sign_in_with_password({"email": email, "password": password})

