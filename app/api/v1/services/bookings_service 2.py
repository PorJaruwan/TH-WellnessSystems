
#from fastapi.encoders import jsonable_encoder
# from app.core.config import get_settings
# settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config


# app/api/v1/services/bookings_service.py

from datetime import date, time, datetime, timedelta
from typing import Dict, List, Union  # ✅ เพิ่ม Union
from uuid import UUID
from fastapi import HTTPException
from app.services.supabase_client import supabase

from app.api.v1.models.bookings_model import (
    PatientListResponse,
    PatientItem,
    StaffListResponse,
    StaffItem,
    BuildingListResponse,
    BuildingItem,
    RoomListResponse,
    RoomItem,
    BookingGridResponse,
    BookingGridRoom,
    BookingGridTimeRow,
    BookingGridSlot,
    BookingCreate,
    BookingCreateResponse,
    BookingDetail,
    BookingUpdateNote,
    BookingHistoryResponse,
    BookingHistoryItem,
    BookingSearchResponse,
    BookingListItem,
    AvailabilityResponse,
    AvailableSlot,
    BookingGridFlatItem,
    BookingGridFlatData,
    BookingGridFlatResponse,
    BookingGridColumnsResponse,
    BookingGridColumn,
    BookingGridCell,
    BookingGridColumnsRow,
)


# ---------- Helpers ----------

def _time_range(start: time, end: time, slot_min: int) -> List[time]:
    times: List[time] = []
    current_dt = datetime.combine(date.today(), start)
    end_dt = datetime.combine(date.today(), end)
    delta = timedelta(minutes=slot_min)
    while current_dt < end_dt:
        times.append(current_dt.time())
        current_dt += delta
    return times


def _format_time(t: time) -> str:
    return t.strftime("%H:%M")


def _status_label(status: str) -> str:
    s = (status or "").strip().lower()
    return {
        "pending": "Pending",
        "booked": "Booked",
        "in_progress": "In Progress",
        "completed": "Completed",
        "done": "Done",
        "no_show": "No Show",
        "cancelled": "Cancelled",
        "available": "Available",
        "locked": "Lock",
        "closed": "Closed",
    }.get(s, s.replace("_", " ").title())


def _handle_supabase_error(res, context: str):
    if getattr(res, "error", None):
        detail = getattr(res.error, "message", str(res.error))
        raise HTTPException(status_code=500, detail=f"{context}: {detail}")


# ---------- Lookup: Patients ----------

async def search_patients_service(
    *,
    patient_code: str | None,
    page: int,
    page_size: int,
) -> PatientListResponse:
    from_idx = (page - 1) * page_size
    to_idx = from_idx + page_size - 1
    keyword = (patient_code or "").strip()

    query = supabase.table("patients").select(
        "id,patient_code,full_name_lo,telephone,email",
        count="exact",
    )

    if keyword:
        or_filter = (
            f"patient_code.ilike.%{keyword}%,"
            f"full_name_lo.ilike.%{keyword}%,"
            f"telephone.ilike.%{keyword}%,"
            f"email.ilike.%{keyword}%"
        )
        query = query.or_(or_filter)

    res = query.order("full_name_lo").range(from_idx, to_idx).execute()
    _handle_supabase_error(res, "search_patients")

    rows = res.data or []
    total = res.count or 0

    items = [
        PatientItem(
            id=row["id"],
            patient_code=row.get("patient_code") or "",
            full_name_lo=row.get("full_name_lo") or "",
            telephone=row.get("telephone"),
            email=row.get("email"),
        )
        for row in rows
    ]

    return PatientListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


# ---------- Lookup: Staff ----------

async def search_staff_service(
    *,
    staff_name: str,
    role: str | None,
    page: int,
    page_size: int,
) -> StaffListResponse:
    from_idx = (page - 1) * page_size
    to_idx = from_idx + page_size - 1

    staff_name = staff_name or ""
    role = role or ""

    query = supabase.table("staff").select(
        "id,staff_name,role,specialty",
        count="exact",
    )

    if role:
        query = query.eq("role", role)

    if staff_name:
        query = query.ilike("staff_name", f"%{staff_name}%")

    res = query.order("staff_name").range(from_idx, to_idx).execute()
    _handle_supabase_error(res, "search_staff")

    rows = res.data or []
    total = res.count or 0

    items = [
        StaffItem(
            id=row["id"],
            staff_name=row.get("staff_name") or "",
            role=row.get("role"),
            specialty=row.get("specialty"),
        )
        for row in rows
    ]

    return StaffListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


# ---------- Lookup: Buildings / Rooms ----------

async def get_buildings_service(
    *,
    location_id: UUID,
    company_code: str | None = None,
) -> BuildingListResponse:
    query = supabase.table("buildings").select("id,building_name")

    query = query.eq("location_id", str(location_id))
    if company_code is not None:
        query = query.eq("company_code", company_code)

    res = query.order("building_name").execute()
    _handle_supabase_error(res, "get_buildings")

    rows = res.data or []

    items = [
        BuildingItem(id=row["id"], building_name=row["building_name"])
        for row in rows
    ]
    return BuildingListResponse(items=items)


async def get_rooms_service(
    *,
    building_id: UUID,
) -> RoomListResponse:
    res = (
        supabase.table("rooms")
        .select("id,room_name,room_type_id")
        .eq("building_id", str(building_id))
        .order("room_name")
        .execute()
    )
    _handle_supabase_error(res, "get_rooms")

    rows = res.data or []

    items = [
        RoomItem(
            id=row["id"],
            room_name=row["room_name"],
            room_type_id=row["room_type_id"],
        )
        for row in rows
    ]
    return RoomListResponse(items=items)


# ---------- Booking Grid (ใช้ booking_grid_view + config) ----------
async def get_booking_grid_service(
    *,
    booking_date: date,
    company_code: str,
    location_id: UUID,
    building_id: UUID,
    view_mode: str = "full",
    page: int = 1,
    format: str = "grid",
    columns: int | None = None,
) -> Union[BookingGridResponse, BookingGridFlatResponse, BookingGridColumnsResponse]:
    # 1) max_columns จาก booking_view_config
    cfg_res = (
        supabase.table("booking_view_config")
        .select("max_columns")
        .eq("company_code", company_code)
        .eq("location_id", str(location_id))
        .eq("building_id", str(building_id))
        .eq("is_active", True)
        .order("is_default", desc=True)
        .order("created_at")
        .limit(1)
        .execute()
    )
    _handle_supabase_error(cfg_res, "booking_view_config")
    cfg_row = (cfg_res.data or [None])[0]
    max_columns = cfg_row["max_columns"] if cfg_row and cfg_row.get("max_columns") else 5
    # ✅ parameter columns มาก่อน ถ้ามี
    max_columns = columns or max_columns

    # 2) exception ของวันนั้น
    exc_res = (
        supabase.table("booking_timeslot_exception")
        .select("time_from,time_to,slot_min,is_closed")
        .eq("company_code", company_code)
        .eq("location_id", str(location_id))
        .eq("building_id", str(building_id))
        .eq("date", booking_date.isoformat())
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    _handle_supabase_error(exc_res, "booking_timeslot_exception")
    exc_row = (exc_res.data or [None])[0]

    if exc_row and exc_row.get("is_closed"):
        raise HTTPException(
            status_code=200,
            detail=f"Booking closed for {booking_date.isoformat()}",
        )

    if exc_row and exc_row.get("time_from") and exc_row.get("time_to"):
        time_from = time.fromisoformat(exc_row["time_from"])
        time_to = time.fromisoformat(exc_row["time_to"])
        slot_min = exc_row.get("slot_min") or 30
    else:
        cfg2_res = (
            supabase.table("booking_timeslot_config")
            .select("time_from,time_to,slot_min")
            .eq("company_code", company_code)
            .eq("location_id", str(location_id))
            .eq("building_id", str(building_id))
            .eq("is_active", True)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        _handle_supabase_error(cfg2_res, "booking_timeslot_config")
        cfg2_row = (cfg2_res.data or [None])[0]
        if not cfg2_row:
            time_from = time(9, 0)
            time_to = time(17, 0)
            slot_min = 30
        else:
            time_from = time.fromisoformat(cfg2_row["time_from"])
            time_to = time.fromisoformat(cfg2_row["time_to"])
            slot_min = cfg2_row.get("slot_min") or 30

    # 3) am/pm
    if view_mode in ("am", "pm"):
        start_dt = datetime.combine(date.today(), time_from)
        end_dt = datetime.combine(date.today(), time_to)
        mid_dt = start_dt + (end_dt - start_dt) / 2
        mid = mid_dt.time()
        if view_mode == "am":
            time_to = mid
        else:
            time_from = mid

    # 4) rooms (paginate columns)
    rooms_res = (
        supabase.table("rooms")
        .select("id,room_name")
        .eq("building_id", str(building_id))
        .eq("is_active", True)
        .order("room_name")
        .execute()
    )
    _handle_supabase_error(rooms_res, "rooms for grid")
    all_rooms = rooms_res.data or []
    if not all_rooms:
        raise HTTPException(status_code=200, detail="No rooms for this building")

    total_rooms = len(all_rooms)
    total_pages = (total_rooms + max_columns - 1) // max_columns or 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * max_columns
    end_idx = start_idx + max_columns
    rooms_slice = all_rooms[start_idx:end_idx]

    rooms_out: List[BookingGridRoom] = [
        BookingGridRoom(room_id=row["id"], room_name=row["room_name"])
        for row in rooms_slice
    ]

    # 5) bookings จาก view
    grid_res = (
        supabase.table("booking_grid_view")
        .select(
            "booking_id,room_id,start_time,end_time,status,"
            "patient_name,doctor_name,service_name"
        )
        .eq("company_code", company_code)
        .eq("location_id", str(location_id))
        .eq("building_id", str(building_id))
        .eq("booking_date", booking_date.isoformat())
        .execute()
    )
    _handle_supabase_error(grid_res, "booking_grid_view")
    rows = grid_res.data or []

    booking_map: Dict[tuple, dict] = {}
    for row in rows:
        room_id = str(row["room_id"])
        start_t = time.fromisoformat(row["start_time"])
        end_t = time.fromisoformat(row["end_time"])

        # fill every slot between start_time (inclusive) and end_time (exclusive)
        cur_dt = datetime.combine(date.today(), start_t)
        end_dt = datetime.combine(date.today(), end_t)
        step = timedelta(minutes=slot_min)
        while cur_dt < end_dt:
            booking_map[(room_id, cur_dt.time())] = row
            cur_dt += step

    time_points = _time_range(time_from, time_to, slot_min)

    # ✅ 6) เลือกรูปแบบ response
    if format == "columns":
        # header meta
        columns_meta: List[BookingGridColumn] = [
            BookingGridColumn(col=i + 1, room_id=r.room_id, room_name=r.room_name)
            for i, r in enumerate(rooms_out)
        ]

        rows_out: List[BookingGridColumnsRow] = []
        for t in time_points:
            row_dict = {"time": _format_time(t)}

            for i, room in enumerate(rooms_out, start=1):
                key = f"col{i}"
                b_row = booking_map.get((str(room.room_id), t))

                if b_row:
                    status = b_row["status"]
                    cell = BookingGridCell(
                        room_id=room.room_id,
                        status=status,
                        status_label=_status_label(status),
                        booking_id=b_row["booking_id"],
                        patient_name=b_row.get("patient_name"),
                        doctor_name=b_row.get("doctor_name"),
                        service_name=b_row.get("service_name"),
                    )
                else:
                    cell = BookingGridCell(
                        room_id=room.room_id,
                        status="available",
                        status_label=_status_label("available"),
                    )

                row_dict[key] = cell.dict()

            rows_out.append(BookingGridColumnsRow(**row_dict))

        return BookingGridColumnsResponse(
            date=booking_date,
            time_from=_format_time(time_from),
            time_to=_format_time(time_to),
            slot_min=slot_min,
            page=page,
            total_pages=total_pages,
            columns=columns_meta,
            rows=rows_out,
        )

    if format == "grid":
        timeslots_out: List[BookingGridTimeRow] = []

        for t in time_points:
            slots_row: List[BookingGridSlot] = []
            for room in rooms_out:
                key = (str(room.room_id), t)
                b_row = booking_map.get(key)

                if b_row:
                    status = b_row["status"]
                    slots_row.append(
                        BookingGridSlot(
                            room_id=room.room_id,
                            status=status,
                            booking_id=b_row["booking_id"],
                            patient_name=b_row["patient_name"],
                            doctor_name=b_row["doctor_name"],
                            service_name=b_row["service_name"],
                            status_label=_status_label(status),
                        )
                    )
                else:
                    slots_row.append(
                        BookingGridSlot(
                            room_id=room.room_id,
                            status="available",
                            booking_id=None,
                            patient_name=None,
                            doctor_name=None,
                            service_name=None,
                            status_label="Available",
                        )
                    )

            timeslots_out.append(
                BookingGridTimeRow(time=_format_time(t), slots=slots_row)
            )

        return BookingGridResponse(
            date=booking_date,
            time_from=_format_time(time_from),
            time_to=_format_time(time_to),
            slot_min=slot_min,
            rooms=rooms_out,
            timeslots=timeslots_out,
            page=page,
            total_pages=total_pages,
        )

    # else: format == "flat"
    items_out: List[BookingGridFlatItem] = []

    for t in time_points:
        t_str = _format_time(t)
        for room in rooms_out:
            key = (str(room.room_id), t)
            b_row = booking_map.get(key)

            if b_row:
                status = b_row["status"]
                items_out.append(
                    BookingGridFlatItem(
                        time=t_str,
                        room_id=room.room_id,
                        room_name=room.room_name,
                        status=status,
                        status_label=_status_label(status),
                        booking_id=b_row["booking_id"],
                        patient_name=b_row["patient_name"],
                        doctor_name=b_row["doctor_name"],
                        service_name=b_row["service_name"],
                    )
                )
            else:
                items_out.append(
                    BookingGridFlatItem(
                        time=t_str,
                        room_id=room.room_id,
                        room_name=room.room_name,
                        status="available",
                        status_label="Available",
                        booking_id=None,
                        patient_name=None,
                        doctor_name=None,
                        service_name=None,
                    )
                )

    data = BookingGridFlatData(
        date=booking_date,
        time_from=_format_time(time_from),
        time_to=_format_time(time_to),
        slot_min=slot_min,
        rooms=rooms_out,
        page=page,
        total_pages=total_pages,
        total=len(items_out),
        items=items_out,
    )

    return BookingGridFlatResponse(
        status="success",
        message="Data retrieved successfully.",
        data=data,
    )

# ---------- Booking CRUD / Status / History ----------

async def create_booking_service(
    booking: BookingCreate,
) -> BookingCreateResponse:
    try:
        start_t = datetime.strptime(booking.start_time, "%H:%M").time()
        end_t = datetime.strptime(booking.end_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="start_time and end_time must be in 'HH:MM' format",
        )

    now = datetime.utcnow().isoformat()

    payload = {
        "resource_track_id": str(booking.resource_track_id),
        "company_code": booking.company_code,
        "location_id": str(booking.location_id),
        "building_id": str(booking.building_id),
        "room_id": str(booking.room_id),
        "patient_id": str(booking.patient_id),
        "primary_person_id": str(booking.primary_person_id),
        "service_id": str(booking.service_id),
        "booking_date": booking.booking_date.isoformat()
        if isinstance(booking.booking_date, date)
        else booking.booking_date,
        "start_time": start_t.isoformat(),
        "end_time": end_t.isoformat(),
        "source_of_ad": booking.source_of_ad,
        "note": booking.note,
        "status": "booked",
        "created_at": now,
        "updated_at": now,
    }

    res = (
        supabase.table("bookings")
        .insert(payload)
        .select("id,status")
        .execute()
    )
    _handle_supabase_error(res, "create_booking")

    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create booking")

    row = res.data[0]
    return BookingCreateResponse(
        id=row["id"],
        status=row["status"],
    )


async def get_booking_detail_service(
    *,
    booking_id: UUID,
) -> BookingDetail:
    # แนะนำให้มี view ชื่อ booking_detail_view ใน DB
    # ซึ่งรวม join ตามที่เดิมใช้ใน SQL
    res = (
        supabase.table("booking_detail_view")
        .select(
            "id,company_code,location_id,building_id,booking_date,"
            "start_time,end_time,status,room_id,room_name,"
            "patient_id,patient_name,doctor_id,doctor_name,"
            "service_id,service_name,note"
        )
        .eq("id", str(booking_id))
        .single()
        .execute()
    )
    _handle_supabase_error(res, "booking_detail_view")

    if not res.data:
        raise HTTPException(status_code=404, detail="Booking not found")

    row = res.data

    return BookingDetail(
        id=row["id"],
        company_code=row["company_code"],
        location_id=row["location_id"],
        building_id=row["building_id"],
        booking_date=date.fromisoformat(row["booking_date"]),
        start_time=time.fromisoformat(row["start_time"]).strftime("%H:%M"),
        end_time=time.fromisoformat(row["end_time"]).strftime("%H:%M"),
        status=row["status"],
        room_id=row["room_id"],
        room_name=row["room_name"],
        patient_id=row["patient_id"],
        patient_name=row["patient_name"],
        doctor_id=row["doctor_id"],
        doctor_name=row["doctor_name"],
        service_id=row["service_id"],
        service_name=row["service_name"],
        note=row["note"],
    )


async def update_booking_note_service(
    *,
    booking_id: UUID,
    body: BookingUpdateNote,
):
    res = (
        supabase.table("bookings")
        .update({"note": body.note, "updated_at": datetime.utcnow().isoformat()})
        .eq("id", str(booking_id))
        .execute()
    )
    _handle_supabase_error(res, "update_booking_note")
    if not res.data:
        raise HTTPException(status_code=404, detail="Booking not found")


async def checkin_booking_service(
    *,
    booking_id: UUID,
    user_id: UUID,
    note: str | None,
):
    # update booking status
    res = (
        supabase.table("bookings")
        .update(
            {
                "status": "in_progress",
                "updated_at": datetime.utcnow().isoformat(),
            }
        )
        .eq("id", str(booking_id))
        .select("status")
        .execute()
    )
    _handle_supabase_error(res, "checkin_booking")

    if not res.data:
        raise HTTPException(status_code=404, detail="Booking not found")

    # insert history
    hist_payload = {
        "booking_id": str(booking_id),
        "old_status": "booked",
        "new_status": "in_progress",
        "changed_by": str(user_id),
        "note": note,
    }
    hist_res = supabase.table("booking_status_history").insert(hist_payload).execute()
    _handle_supabase_error(hist_res, "insert_booking_history_checkin")

    return {"id": booking_id, "status": "in_progress"}


async def cancel_booking_service(
    *,
    booking_id: UUID,
    user_id: UUID,
    reason: str | None,
    note: str | None,
):
    res = (
        supabase.table("bookings")
        .update(
            {
                "status": "cancelled",
                "cancel_reason": reason,
                "updated_at": datetime.utcnow().isoformat(),
            }
        )
        .eq("id", str(booking_id))
        .select("status")
        .execute()
    )
    _handle_supabase_error(res, "cancel_booking")

    if not res.data:
        raise HTTPException(status_code=404, detail="Booking not found")

    hist_payload = {
        "booking_id": str(booking_id),
        "old_status": "booked",
        "new_status": "cancelled",
        "changed_by": str(user_id),
        "note": note or reason,
    }
    hist_res = supabase.table("booking_status_history").insert(hist_payload).execute()
    _handle_supabase_error(hist_res, "insert_booking_history_cancel")

    return {"id": booking_id, "status": "cancelled"}


async def get_booking_history_service(
    *,
    booking_id: UUID,
) -> BookingHistoryResponse:
    res = (
        supabase.table("booking_status_history")
        .select("id,old_status,new_status,changed_at,changed_by,note")
        .eq("booking_id", str(booking_id))
        .order("changed_at", desc=True)
        .execute()
    )
    _handle_supabase_error(res, "get_booking_history")

    rows = res.data or []

    items = [
        BookingHistoryItem(
            id=row["id"],
            old_status=row["old_status"],
            new_status=row["new_status"],
            changed_at=datetime.fromisoformat(row["changed_at"]).isoformat(),
            changed_by=row["changed_by"],
            note=row["note"],
        )
        for row in rows
    ]

    return BookingHistoryResponse(booking_id=booking_id, items=items)


# ---------- Booking Search (ใช้ booking_grid_view) ----------

async def search_bookings_service(
    *,
    q: str | None,
    company_code: str | None,
    location_id: UUID | None,
    booking_date: date | None,
    page: int,
    page_size: int,
) -> BookingSearchResponse:
    from_idx = (page - 1) * page_size
    to_idx = from_idx + page_size - 1

    keyword = (q or "").strip()

    # 🔹 พยายาม parse เป็น UUID ถ้าได้ = ใช้เป็น patient_id
    patient_uuid: UUID | None = None
    if keyword:
        try:
            patient_uuid = UUID(keyword)
        except ValueError:
            patient_uuid = None

    query = supabase.table("booking_grid_view").select(
        "booking_id,booking_date,start_time,end_time,status,"
        "room_name,patient_name,doctor_name,service_name",
        count="exact",
    )

    if company_code:
        query = query.eq("company_code", company_code)
    if location_id:
        query = query.eq("location_id", str(location_id))
    if booking_date:
        query = query.eq("booking_date", booking_date.isoformat())

    # ✅ ถ้า q เป็น UUID → filter ด้วย patient_id
    if patient_uuid:
        query = query.eq("patient_id", str(patient_uuid))
    # ❗ ถ้าไม่ใช่ UUID → ใช้เป็น keyword ค้นชื่อ / service แบบเดิม
    elif keyword:
        or_filter = (
            f"patient_name.ilike.%{keyword}%,"
            f"doctor_name.ilike.%{keyword}%,"
            f"service_name.ilike.%{keyword}%"
        )
        query = query.or_(or_filter)

    res = (
        query
        .order("booking_date", desc=True)
        .order("start_time")
        .range(from_idx, to_idx)
        .execute()
    )
    _handle_supabase_error(res, "search_bookings")

    rows = res.data or []
    total = res.count or 0

    items = []
    for row in rows:
        items.append(
            BookingListItem(
                id=row["booking_id"],
                booking_date=date.fromisoformat(row["booking_date"]),
                start_time=time.fromisoformat(row["start_time"]).strftime("%H:%M"),
                end_time=time.fromisoformat(row["end_time"]).strftime("%H:%M"),
                status=row["status"],
                room_name=row["room_name"],
                patient_name=row["patient_name"],
                doctor_name=row["doctor_name"],
                service_name=row["service_name"],
            )
        )

    return BookingSearchResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )

###===old version - befor add patient_id
# async def search_bookings_service(
#     *,
#     q: str | None,
#     company_code: str | None,
#     location_id: UUID | None,
#     booking_date: date | None,
#     page: int,
#     page_size: int,
# ) -> BookingSearchResponse:
#     from_idx = (page - 1) * page_size
#     to_idx = from_idx + page_size - 1

#     keyword = (q or "").strip()

#     query = supabase.table("booking_grid_view").select(
#         "booking_id,booking_date,start_time,end_time,status,"
#         "room_name,patient_name,doctor_name,service_name",
#         count="exact",
#     )

#     if company_code:
#         query = query.eq("company_code", company_code)
#     if location_id:
#         query = query.eq("location_id", str(location_id))
#     if booking_date:
#         query = query.eq("booking_date", booking_date.isoformat())

#     if keyword:
#         or_filter = (
#             f"patient_name.ilike.%{keyword}%,"
#             f"doctor_name.ilike.%{keyword}%,"
#             f"service_name.ilike.%{keyword}%"
#         )
#         query = query.or_(or_filter)

#     res = (
#         query
#         .order("booking_date", desc=True)
#         .order("start_time")
#         .range(from_idx, to_idx)
#         .execute()
#     )
#     _handle_supabase_error(res, "search_bookings")

#     rows = res.data or []
#     total = res.count or 0

#     items = []
#     for row in rows:
#         items.append(
#             BookingListItem(
#                 id=row["booking_id"],
#                 booking_date=date.fromisoformat(row["booking_date"]),
#                 start_time=time.fromisoformat(row["start_time"]).strftime("%H:%M"),
#                 end_time=time.fromisoformat(row["end_time"]).strftime("%H:%M"),
#                 status=row["status"],
#                 room_name=row["room_name"],
#                 patient_name=row["patient_name"],
#                 doctor_name=row["doctor_name"],
#                 service_name=row["service_name"],
#             )
#         )

#     return BookingSearchResponse(
#         items=items,
#         page=page,
#         page_size=page_size,
#         total=total,
#     )

# ---------- Availability (simple sample – ไม่แตะ DB) ----------

async def get_resource_availability_service(
    *,
    resource_track_id: UUID,
    date_: date,
) -> AvailabilityResponse:
    start = time(9, 0)
    end = time(17, 0)
    slot_min = 30

    time_points = _time_range(start, end, slot_min)
    slots: List[AvailableSlot] = []
    for t in time_points:
        end_dt = (datetime.combine(date.today(), t) + timedelta(minutes=slot_min)).time()
        slots.append(
            AvailableSlot(
                start_time=_format_time(t),
                end_time=_format_time(end_dt),
            )
        )

    return AvailabilityResponse(
        resource_track_id=resource_track_id,
        date=date_,
        available_slots=slots,
    )


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
