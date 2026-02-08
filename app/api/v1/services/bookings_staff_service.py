# app/api/v1/services/bookings_staff_service.py

from uuid import UUID
from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

# ==============================
#booking staff
# ==============================
def create_booking_staff(data: dict):
    return supabase.table("booking_staff").insert(data).execute()

def get_all_booking_staff():
    return supabase.table("booking_staff").select("*").order("booking_id", desc=False).execute()

def get_booking_staff_by_id(booking_staff_id: UUID):
    return supabase.table("booking_staff").select("*").eq("id", str(booking_staff_id)).execute()

def update_booking_staff_by_id(booking_staff_id: UUID, updated_data: dict):
    return supabase.table("booking_staff").update(updated_data).eq("id", str(booking_staff_id)).execute()

def delete_booking_staff_by_id(booking_staff_id: UUID):
    return supabase.table("booking_staff").delete().eq("id", str(booking_staff_id)).execute()

# app/api/v1/services/booking_staff_service.py
def get_booking_staff_by_booking_id(booking_id: UUID, role: str | None = None):
    q = (
        supabase
        .table("booking_staff")
        .select("*")
        .eq("booking_id", str(booking_id))
    )
    if role:
        q = q.eq("role", role)

    # เรียงให้ deterministic (ปรับตามต้องการ)
    return q.order("is_primary", desc=True).order("created_at", desc=True).execute()
