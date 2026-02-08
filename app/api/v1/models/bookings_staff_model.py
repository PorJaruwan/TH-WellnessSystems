# app/models/booking_staff_models.py

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total: int


# ==============================
#Booking Staff
#===============================
class BookingStaffCreateModel(BaseModel):
    id: UUID
    booking_id: str
    staff_id: str
    role: str
    is_primary: bool
    note: str
    is_active: bool
    #created_at: datetime
    #updated_at: datetime

class BookingStaffUpdateModel(BaseModel):
    booking_id: str
    staff_id: str
    role: str
    is_primary: bool
    note: str
    is_active: bool
    #updated_at: datetime

class BookingStaffQueryByBookingId(BaseModel):
    booking_id: UUID = Field(..., description="Booking UUID")
    role: Optional[str] = Field(None, description="Optional role filter เช่น doctor/nurse")

class BookingStaffListResponse(BaseModel):
    booking_staff: List[Any] = []  # ถ้าคุณมี schema ของ row ชัดเจน ค่อยเปลี่ยนเป็น List[BookingStaffOut]
