# /api/v1/auth_supabase/resend-confirm
import os, requests
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/api/v1/auth_supabase",
    tags=["User_Settings"]
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")
REDIRECT_TO = os.getenv("EMAIL_REDIRECT_TO", "http://localhost:3000/auth/callback")

@router.post("/resend-confirm")
def resend_confirm(email: str):
  url = f"{SUPABASE_URL}/auth/v1/resend"
  headers = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
  }
  body = {"type": "signup", "email": email, "redirect_to": REDIRECT_TO}
  r = requests.post(url, headers=headers, json=body, timeout=10)
  if r.status_code >= 300:
    raise HTTPException(status_code=r.status_code, detail=r.text)
  return {"success": True}
