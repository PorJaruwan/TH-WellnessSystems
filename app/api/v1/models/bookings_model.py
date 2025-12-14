
# app/models/booking_models.py
from datetime import date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


# ---------- Lookup Models ----------

class PatientItem(BaseModel):
    id: UUID
    patient_code: Optional[str] = None
    full_name_lo: str
    telephone: Optional[str] = None
    email: Optional[str] = None


class StaffItem(BaseModel):
    id: UUID
    staff_name: str
    role: Optional[str] = None
    specialty: Optional[str] = None


class BuildingItem(BaseModel):
    id: UUID
    building_name: str


class RoomItem(BaseModel):
    id: UUID
    room_name: str
    room_type_id: Optional[UUID] = None


class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total: int


class PatientListResponse(PaginatedResponse):
    items: List[PatientItem]


class StaffListResponse(PaginatedResponse):
    items: List[StaffItem]


class BuildingListResponse(BaseModel):
    items: List[BuildingItem]


class RoomListResponse(BaseModel):
    items: List[RoomItem]


# ---------- Booking Grid Models ----------
class BookingGridSlot(BaseModel):
    room_id: UUID
    status: str                      # booked / in_progress / completed / available / locked / closed
    booking_id: Optional[UUID] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    service_name: Optional[str] = None
    status_label: Optional[str] = None
    
class BookingGridTimeRow(BaseModel):
    time: str                        # "HH:MM"
    slots: List[BookingGridSlot]


class BookingGridRoom(BaseModel):
    room_id: UUID
    room_name: str

class BookingGridResponse(BaseModel):
    date: date
    time_from: str
    time_to: str
    slot_min: int
    rooms: List[BookingGridRoom]
    timeslots: List[BookingGridTimeRow]
    page: int
    total_pages: int

# ---------- Booking CRUD / Detail / Status ----------
class BookingCreate(BaseModel):
    resource_track_id: Optional[UUID] = None
    company_code: str
    location_id: UUID
    building_id: UUID
    room_id: UUID
    patient_id: UUID
    primary_person_id: UUID
    service_id: UUID
    booking_date: date
    start_time: str      # format "HH:MM"
    end_time: str        # format "HH:MM"
    source_of_ad: Optional[str] = None
    note: Optional[str] = None

###Json-Request body:
# {
#   "resource_track_id": "0903050b-e493-485f-acac-bb2bf5b3ea09",
#   "company_code": "LNV",
#   "location_id": "0903050b-e493-485f-acac-bb2bf5b3ea09",
#   "building_id": "627b339b-0649-4cb9-8e1f-b890f1d3fe3c",
#   "room_id": "14176cc5-4ed0-4527-8fb3-e4eaab1bbdf7",
#   "patient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
#   "primary_person_id": "3c9fc805-a241-416c-9614-6ba879a48b6f",
#   "service_id": "4f12b07d-e6bc-46e2-bcdb-7a680d18a249",
#   "booking_date": "2025-12-03",
#   "start_time": "10:00",
#   "end_time": "10:30",
#   "source_of_ad": "online",     
#   "note": "test booking-3"
# }


class BookingCreateResponse(BaseModel):
    id: UUID
    status: str


class BookingDetail(BaseModel):
    id: UUID
    company_code: str
    location_id: UUID
    building_id: UUID
    booking_date: date
    start_time: str
    end_time: str
    status: str
    room_id: UUID
    room_name: str
    patient_id: UUID
    patient_name: str
    doctor_id: UUID
    doctor_name: str
    service_id: UUID
    service_name: str
    note: Optional[str] = None


class BookingUpdateNote(BaseModel):
    note: str


class BookingHistoryItem(BaseModel):
    id: UUID
    old_status: Optional[str] = None
    new_status: str
    changed_at: str
    changed_by: Optional[UUID] = None
    note: Optional[str] = None


class BookingHistoryResponse(BaseModel):
    booking_id: UUID
    items: List[BookingHistoryItem]


class BookingListItem(BaseModel):
    id: UUID
    booking_date: date
    start_time: str
    end_time: str
    status: str
    room_name: str
    patient_name: str
    doctor_name: str
    service_name: str


class BookingSearchResponse(PaginatedResponse):
    items: List[BookingListItem]


# ---------- Availability ----------

class AvailableSlot(BaseModel):
    start_time: str
    end_time: str


class AvailabilityResponse(BaseModel):
    resource_track_id: UUID
    date: date
    available_slots: List[AvailableSlot]

# ---------- เพิ่มท้ายไฟล์ ----------
class BookingGridFlatItem(BaseModel):
    time: str                        # "HH:MM"
    room_id: UUID
    room_name: str

    status: str
    status_label: Optional[str] = None

    booking_id: Optional[UUID] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    service_name: Optional[str] = None


class BookingGridFlatData(BaseModel):
    date: date
    time_from: str
    time_to: str
    slot_min: int

    page: int
    total_pages: int
    total: int                        # จำนวน items ทั้งหมดในหน้านี้

    rooms: List[BookingGridRoom]      # ใช้ของเดิมได้เลย
    items: List[BookingGridFlatItem]


class BookingGridFlatResponse(BaseModel):
    status: str
    message: str
    data: BookingGridFlatData