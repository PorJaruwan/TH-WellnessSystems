# from supabase import create_client, Client
# from app.core.config import get_settings

# settings = get_settings()
# supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# app/services/supabase_client.py
from app.core.config import get_settings
from supabase import create_client, Client

_settings = get_settings()

if not _settings.SUPABASE_URL or not _settings.SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

supabase: Client = create_client(_settings.SUPABASE_URL, _settings.SUPABASE_KEY)


##### Old Version-2025-07-01
# import os
# from dotenv import load_dotenv
# from supabase import create_client, Client
# # โหลด environment จาก .env
# load_dotenv()
# # สร้าง Supabase Client จาก environment
# supabase_url = os.getenv("SUPABASE_URL")
# supabase_key = os.getenv("SUPABASE_KEY")
# if not supabase_url or not supabase_key:
#     raise RuntimeError("Supabase URL or KEY not found in environment variables.")
# supabase: Client = create_client(supabase_url, supabase_key)

##### Test read .env-2025-07-01
# print("✅ SUPABASE_URL =", supabase_url)
# if supabase_key:
#     print("✅ SUPABASE_KEY =", supabase_key[:10], "...(truncated)") # ตรวจสอบไม่ให้แสดงทั้ง key
# else:
#     print("❌ SUPABASE_KEY is missing. Check your .env file or environment.")

# ทดสอบ key
# supabase_key = os.getenv(
#    "SUPABASE_SERVICE_KEY","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJza3BhcXh2c3BoZ2hubXJka3h6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MDg5NjAxMCwiZXhwIjoyMDU2NDcyMDEwfQ.2h7QmXjHMNMpCouachiyvy0N2adwflYzjBkDqZk6kVU"
# )