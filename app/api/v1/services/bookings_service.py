# app/services/booking_service.py
from app.services.supabase_client import supabase
from datetime import date, time, datetime, timedelta
from typing import List, Dict
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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
)


# ---------- Helper ----------

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


# ---------- Lookup Services ----------
async def search_patients_service(
    db: AsyncSession,
    *,
    patient_code: str | None,
    page: int,
    page_size: int,
) -> PatientListResponse:
    offset = (page - 1) * page_size

    # ใช้เป็น keyword รวม (string เสมอ ไม่ให้เป็น None)
    keyword = (patient_code or "").strip()

    sql = text(
        """
        SELECT id, patient_code, full_name_lo, telephone, email
        FROM public.patients
        WHERE (
            :keyword = '' OR
            patient_code ILIKE '%' || :keyword || '%' OR
            full_name_lo ILIKE '%' || :keyword || '%' OR
            telephone    ILIKE '%' || :keyword || '%' OR
            email        ILIKE '%' || :keyword || '%'
        )
        ORDER BY full_name_lo
        LIMIT :limit OFFSET :offset;
        """
    )

    count_sql = text(
        """
        SELECT COUNT(*)
        FROM public.patients
        WHERE (
            :keyword = '' OR
            patient_code ILIKE '%' || :keyword || '%' OR
            full_name_lo ILIKE '%' || :keyword || '%' OR
            telephone    ILIKE '%' || :keyword || '%' OR
            email        ILIKE '%' || :keyword || '%'
        );
        """
    )

    params = {
        "keyword": keyword,
        "limit": page_size,
        "offset": offset,
    }

    rows = (await db.execute(sql, params)).mappings().all()
    total = (await db.execute(count_sql, params)).scalar_one()

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

#####
# async def search_patients_service(
#     db: AsyncSession,
#     *,
#     patient_code: str,
#     page: int,
#     page_size: int,
# ) -> PatientListResponse:
#     offset = (page - 1) * page_size

#     patient_code = patient_code or ""   # ✅ บังคับให้ code เป็น string เสมอ (ไม่ให้เป็น None)

#     sql = text(
#         """
#         SELECT id, patient_code, full_name_lo, telephone, email
#         FROM public.patients
#         WHERE (:patient_code = '' OR patient_code ILIKE '%' || :patient_code || '%')
#         ORDER BY full_name_lo
#         LIMIT :limit OFFSET :offset;
#         """
#     )

#     count_sql = text(
#         """
#         SELECT COUNT(*)
#         FROM public.patients
#         WHERE (:patient_code = '' OR patient_code ILIKE '%' || :patient_code || '%');
#         """
#     )

#     params = {
#         "patient_code": patient_code,
#         "limit": page_size,
#         "offset": offset,
#     }

#     rows = (await db.execute(sql, params)).mappings().all()
#     total = (await db.execute(count_sql, {"patient_code": patient_code})).scalar_one()

#     items = [
#         PatientItem(
#             id=row["id"],
#             patient_code=row.get("patient_code") or "",
#             full_name_lo=row.get("full_name_lo") or "",
#             telephone=row.get("telephone"),
#             email=row.get("email"),
#         )
#         for row in rows
#     ]

#     return PatientListResponse(
#         items=items,
#         page=page,
#         page_size=page_size,
#         total=total,
#     )

async def search_staff_service(
    db: AsyncSession,
    *,
    staff_name: str,
    role: str | None,
    page: int,
    page_size: int,
) -> StaffListResponse:
    offset = (page - 1) * page_size

    # ✅ บังคับไม่ให้เป็น None เพื่อกัน AmbiguousParameterError
    staff_name = staff_name or ""
    role = role or ""

    sql = text(
        """
        SELECT id, staff_name, role, specialty
        FROM public.staff
        WHERE (:role = '' OR role = :role)
          AND (:staff_name = '' OR staff_name ILIKE '%' || :staff_name || '%')
        ORDER BY staff_name
        LIMIT :limit OFFSET :offset;
        """
    )

    count_sql = text(
        """
        SELECT COUNT(*)
        FROM public.staff
        WHERE (:role = '' OR role = :role)
          AND (:staff_name = '' OR staff_name ILIKE '%' || :staff_name || '%');
        """
    )

    params = {
        "role": role,
        "staff_name": staff_name,
        "limit": page_size,
        "offset": offset,
    }

    rows = (await db.execute(sql, params)).mappings().all()
    total = (await db.execute(count_sql, {"role": role, "staff_name": staff_name})).scalar_one()

    items = [
        StaffItem(
            id=row["id"],
            # ✅ กันกรณี staff_name ใน DB เป็น NULL
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



async def get_buildings_service(
    db: AsyncSession,
    *,
    location_id: UUID,
    company_code: str | None = None,
) -> BuildingListResponse:

    # ไม่มี company_code -> filter แค่ location_id
    if company_code is None:
        sql = text(
            """
            SELECT id, building_name
            FROM public.buildings
            WHERE location_id = :location_id
            ORDER BY building_name;
            """
        )
        params = {"location_id": str(location_id)}
    else:
        # มี company_code -> filter ทั้ง location_id + company_code
        sql = text(
            """
            SELECT id, building_name
            FROM public.buildings
            WHERE location_id = :location_id
              AND company_code = :company_code
            ORDER BY building_name;
            """
        )
        params = {
            "location_id": str(location_id),
            "company_code": company_code,
        }

    rows = (await db.execute(sql, params)).mappings().all()

    items = [
        BuildingItem(id=row["id"], building_name=row["building_name"])
        for row in rows
    ]
    return BuildingListResponse(items=items)


async def get_rooms_service(
    db: AsyncSession,
    *,
    building_id: UUID,
) -> RoomListResponse:
    sql = text(
        """
        SELECT id, room_name, room_type_id
        FROM public.rooms
        WHERE building_id = :building_id
        ORDER BY room_name;
        """
    )
    rows = (await db.execute(sql, {"building_id": str(building_id)})).mappings().all()
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
    db: AsyncSession,
    *,
    booking_date: date,
    company_code: str,
    location_id: UUID,
    building_id: UUID,
    view_mode: str = "full",
    page: int = 1,
) -> BookingGridResponse:
    # 1) เอา max_columns จาก booking_view_config
    view_cfg_sql = text(
        """
        SELECT max_columns
        FROM public.booking_view_config
        WHERE company_code = :company_code
          AND location_id = :location_id
          AND building_id = :building_id
          AND is_active = TRUE
        ORDER BY is_default DESC, created_at ASC
        LIMIT 1;
        """
    )
    max_columns = (
        await db.execute(
            view_cfg_sql,
            {
                "company_code": company_code,
                "location_id": str(location_id),
                "building_id": str(building_id),
            },
        )
    ).scalar_one_or_none() or 5

    # 2) เอา config slot (รวม exception)
    exc_sql = text(
        """
        SELECT time_from, time_to, slot_min, is_closed
        FROM public.booking_timeslot_exception
        WHERE company_code = :company_code
          AND location_id = :location_id
          AND building_id = :building_id
          AND date = :booking_date
        ORDER BY created_at DESC
        LIMIT 1;
        """
    )
    exc_row = (
        await db.execute(
            exc_sql,
            {
                "company_code": company_code,
                "location_id": str(location_id),
                "building_id": str(building_id),
                "booking_date": booking_date,
            },
        )
    ).mappings().first()

    # ถ้าวันนั้นปิด booking ทั้งวัน
    if exc_row and exc_row["is_closed"]:
        raise HTTPException(
            status_code=200,
            detail=f"Booking closed for {booking_date.isoformat()}",
        )

    # มี exception เฉพาะวัน → ใช้ช่วงเวลา/slot จาก exception
    if exc_row and exc_row["time_from"] and exc_row["time_to"]:
        time_from: time = exc_row["time_from"]
        time_to: time = exc_row["time_to"]
        slot_min: int = exc_row["slot_min"] or 30
    else:
        # ไม่มี exception → ใช้ booking_timeslot_config ปกติ
        cfg_sql = text(
            """
            SELECT time_from, time_to, slot_min
            FROM public.booking_timeslot_config
            WHERE company_code = :company_code
              AND location_id = :location_id
              AND building_id = :building_id
              AND is_active = TRUE
            ORDER BY created_at DESC
            LIMIT 1;
            """
        )
        cfg_row = (
            await db.execute(
                cfg_sql,
                {
                    "company_code": company_code,
                    "location_id": str(location_id),
                    "building_id": str(building_id),
                },
            )
        ).mappings().first()

        if not cfg_row:
            # 🔁 กรณียังไม่มี config → ใช้ค่า default 09:00–17:00, slot 30 นาที
            time_from = time(9, 0)
            time_to = time(17, 0)
            slot_min = 30
        else:
            time_from = cfg_row["time_from"]
            time_to = cfg_row["time_to"]
            slot_min = cfg_row["slot_min"] or 30

    # 3) ปรับตาม view_mode (am / pm / full)
    if view_mode in ("am", "pm"):
        start_dt = datetime.combine(date.today(), time_from)
        end_dt = datetime.combine(date.today(), time_to)
        mid_dt = start_dt + (end_dt - start_dt) / 2
        mid = mid_dt.time()
        if view_mode == "am":
            time_to = mid
        else:
            time_from = mid

    # 4) rooms ตาม building + แบ่ง page ตาม max_columns
    rooms_sql = text(
        """
        SELECT id, room_name
        FROM public.rooms
        WHERE building_id = :building_id
          AND is_active = TRUE
        ORDER BY room_name;
        """
    )
    all_rooms = (
        await db.execute(
            rooms_sql,
            {"building_id": str(building_id)},
        )
    ).mappings().all()

    if not all_rooms:
        raise HTTPException(status_code=200, detail="No rooms for this building")

    total_rooms = len(all_rooms)
    total_pages = (total_rooms + max_columns - 1) // max_columns
    if total_pages == 0:
        total_pages = 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * max_columns
    end_idx = start_idx + max_columns
    rooms_slice = all_rooms[start_idx:end_idx]

    rooms_out: List[BookingGridRoom] = [
        BookingGridRoom(room_id=row["id"], room_name=row["room_name"])
        for row in rooms_slice
    ]

    # 5) ดึง booking จาก view (ไม่ filter room_id ใน SQL แล้ว ค่อย filter ใน Python)
    bookings_sql = text(
        """
        SELECT
            booking_id,
            room_id,
            start_time,
            end_time,
            status,
            patient_name,
            doctor_name,
            service_name
        FROM public.booking_grid_view
        WHERE company_code = :company_code
          AND location_id = :location_id
          AND building_id = :building_id
          AND booking_date = :booking_date;
        """
    )

    rows = (
        await db.execute(
            bookings_sql,
            {
                "company_code": company_code,
                "location_id": str(location_id),
                "building_id": str(building_id),
                "booking_date": booking_date,
            },
        )
    ).mappings().all()

    # map ใช้ key = (room_id, start_time)
    booking_map: Dict[tuple, dict] = {}
    for row in rows:
        key = (str(row["room_id"]), row["start_time"])
        booking_map[key] = row

    # 6) สร้าง timeslots ตาม config
    time_points = _time_range(time_from, time_to, slot_min)
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
                        status_label=status.replace("_", " ").title(),
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


# ---------- Booking CRUD / Status / Search ----------
async def create_booking_service(
    db: AsyncSession,
    booking: BookingCreate,
) -> BookingCreateResponse:
    # 1) แปลง string "HH:MM" → datetime.time
    try:
        start_t: time = datetime.strptime(booking.start_time, "%H:%M").time()
        end_t: time = datetime.strptime(booking.end_time, "%H:%M").time()
    except ValueError:
        # ถ้า format ไม่ใช่ HH:MM ให้ตอบ 400 กลับไป
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="start_time and end_time must be in 'HH:MM' format",
        )

    sql = text(
        """
        INSERT INTO public.bookings(
          resource_track_id, company_code, location_id, building_id,
          room_id, patient_id, primary_person_id, service_id,
          booking_date, start_time, end_time,
          source_of_ad, note, status, 
          created_at, updated_at
        ) VALUES (
          :resource_track_id, :company_code, :location_id, :building_id,
          :room_id, :patient_id, :primary_person_id, :service_id,
          :booking_date,
          :start_time,
          :end_time,
          :source_of_ad, :note, :status,
          :created_at, :updated_at
        )
        RETURNING id, status;
        """
    )

    now = datetime.utcnow()

    params = {
        "resource_track_id": booking.resource_track_id,
        "company_code": booking.company_code,
        "location_id": booking.location_id,
        "building_id": booking.building_id,
        "room_id": booking.room_id,
        "patient_id": booking.patient_id,
        "primary_person_id": booking.primary_person_id,
        "service_id": booking.service_id,
        "booking_date": booking.booking_date,
        "start_time": start_t,     # ✅ ส่งเป็น datetime.time
        "end_time": end_t,         # ✅ ส่งเป็น datetime.time
        "source_of_ad": booking.source_of_ad,
        "note": booking.note,
        "status": "booked",
        "created_at": now,
        "updated_at": now,
    }

    result = await db.execute(sql, params)
    row = result.mappings().first()
    await db.commit()

    return BookingCreateResponse(
        id=row["id"],
        status=row["status"],
    )


async def get_booking_detail_service(
    db: AsyncSession,
    *,
    booking_id: UUID,
) -> BookingDetail:
    sql = text(
        """
        SELECT
          b.id,
          b.company_code,
          b.location_id,
          b.building_id,
          b.booking_date,
          b.start_time,
          b.end_time,
          b.status,
          b.room_id,
          r.room_name,
          b.patient_id,
          p.full_name_lo AS patient_name,
          b.primary_person_id AS doctor_id,
          s.staff_name AS doctor_name,
          b.service_id,
          sv.service_name,
          b.note
        FROM public.bookings b
        LEFT JOIN public.rooms r    ON r.id  = b.room_id
        LEFT JOIN public.patients p ON p.id  = b.patient_id
        LEFT JOIN public.staff s    ON s.id  = b.primary_person_id
        LEFT JOIN public.services sv ON sv.id = b.service_id
        WHERE b.id = :booking_id;
        """
    )
    row = (await db.execute(sql, {"booking_id": str(booking_id)})).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Booking not found")

    return BookingDetail(
        id=row["id"],
        company_code=row["company_code"],
        location_id=row["location_id"],
        building_id=row["building_id"],
        booking_date=row["booking_date"],
        start_time=row["start_time"].strftime("%H:%M"),
        end_time=row["end_time"].strftime("%H:%M"),
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
    db: AsyncSession,
    *,
    booking_id: UUID,
    body: BookingUpdateNote,
):
    sql = text(
        """
        UPDATE public.bookings
        SET note = :note,
            updated_at = NOW()
        WHERE id = :booking_id;
        """
    )
    await db.execute(sql, {"note": body.note, "booking_id": str(booking_id)})
    await db.commit()


async def checkin_booking_service(
    db: AsyncSession,
    *,
    booking_id: UUID,
    user_id: UUID,
    note: str | None,
):
    sql_booking = text(
        """
        UPDATE public.bookings
        SET status = 'in_progress',
            updated_at = NOW()
        WHERE id = :booking_id
        RETURNING status;
        """
    )
    row = (await db.execute(sql_booking, {"booking_id": str(booking_id)})).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Booking not found")

    sql_hist = text(
        """
        INSERT INTO public.booking_status_history(
          booking_id, old_status, new_status, changed_by, note
        )
        VALUES (:booking_id, :old_status, 'in_progress', :changed_by, :note);
        """
    )
    await db.execute(
        sql_hist,
        {
            "booking_id": str(booking_id),
            "old_status": "booked",
            "changed_by": str(user_id),
            "note": note,
        },
    )
    await db.commit()
    return {"id": booking_id, "status": "in_progress"}


async def cancel_booking_service(
    db: AsyncSession,
    *,
    booking_id: UUID,
    user_id: UUID,
    reason: str | None,
    note: str | None,
):
    sql_booking = text(
        """
        UPDATE public.bookings
        SET status = 'cancelled',
            cancel_reason = :reason,
            updated_at = NOW()
        WHERE id = :booking_id
        RETURNING status;
        """
    )
    row = (await db.execute(
        sql_booking,
        {"booking_id": str(booking_id), "reason": reason},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Booking not found")

    sql_hist = text(
        """
        INSERT INTO public.booking_status_history(
          booking_id, old_status, new_status, changed_by, note
        )
        VALUES (:booking_id, :old_status, 'cancelled', :changed_by, :note);
        """
    )
    await db.execute(
        sql_hist,
        {
            "booking_id": str(booking_id),
            "old_status": "booked",
            "changed_by": str(user_id),
            "note": note or reason,
        },
    )
    await db.commit()
    return {"id": booking_id, "status": "cancelled"}


async def get_booking_history_service(
    db: AsyncSession,
    *,
    booking_id: UUID,
) -> BookingHistoryResponse:
    sql = text(
        """
        SELECT id, old_status, new_status,
               changed_at, changed_by, note
        FROM public.booking_status_history
        WHERE booking_id = :booking_id
        ORDER BY changed_at DESC;
        """
    )
    rows = (await db.execute(
        sql,
        {"booking_id": str(booking_id)},
    )).mappings().all()

    items = [
        BookingHistoryItem(
            id=row["id"],
            old_status=row["old_status"],
            new_status=row["new_status"],
            changed_at=row["changed_at"].isoformat(),
            changed_by=row["changed_by"],
            note=row["note"],
        )
        for row in rows
    ]
    return BookingHistoryResponse(booking_id=booking_id, items=items)

#===================================
async def search_bookings_service(
    db: AsyncSession,
    *,
    q: str | None,
    company_code: str | None,
    location_id: UUID | None,
    booking_date: date | None,
    page: int,
    page_size: int,
) -> BookingSearchResponse:
    offset = (page - 1) * page_size

    keyword = q.strip() if q else None
    like_keyword = f"%{keyword}%" if keyword else None

    sql = text(
        """
        SELECT
          b.id,
          b.booking_date,
          b.start_time,
          b.end_time,
          b.status,
          r.room_name,
          p.full_name_lo AS patient_name,
          s.staff_name   AS doctor_name,
          sv.service_name
        FROM public.bookings b
        LEFT JOIN public.rooms    r  ON r.id  = b.room_id
        LEFT JOIN public.patients p  ON p.id  = b.patient_id
        LEFT JOIN public.staff    s  ON s.id  = b.primary_person_id
        LEFT JOIN public.services sv ON sv.id = b.service_id
        WHERE (:company_code IS NULL OR b.company_code = :company_code::text)
          AND (:location_id  IS NULL OR b.location_id  = :location_id::uuid)
          AND (:booking_date IS NULL OR b.booking_date = :booking_date::date)
          AND (
                :keyword IS NULL OR
                p.full_name_lo  ILIKE :like_keyword OR
                s.staff_name    ILIKE :like_keyword OR
                sv.service_name ILIKE :like_keyword
          )
        ORDER BY b.booking_date DESC, b.start_time
        LIMIT :limit OFFSET :offset;
        """
    )

    count_sql = text(
        """
        SELECT COUNT(*)
        FROM public.bookings b
        LEFT JOIN public.patients p ON p.id = b.patient_id
        LEFT JOIN public.staff    s ON s.id = b.primary_person_id
        LEFT JOIN public.services sv ON sv.id = b.service_id
        WHERE (:company_code IS NULL OR b.company_code = :company_code::text)
          AND (:location_id  IS NULL OR b.location_id  = :location_id::uuid)
          AND (:booking_date IS NULL OR b.booking_date = :booking_date::date)
          AND (
                :keyword IS NULL OR
                p.full_name_lo  ILIKE :like_keyword OR
                s.staff_name    ILIKE :like_keyword OR
                sv.service_name ILIKE :like_keyword
          );
        """
    )

    params = {
        "keyword": keyword,
        "like_keyword": like_keyword,
        "company_code": company_code,
        "location_id": str(location_id) if location_id else None,
        "booking_date": booking_date.isoformat() if booking_date else None,
        "limit": page_size,
        "offset": offset,
    }

    rows = (await db.execute(sql, params)).mappings().all()
    total = (await db.execute(count_sql, params)).scalar_one()

    items = [
        BookingListItem(
            id=row["id"],
            booking_date=row["booking_date"],
            start_time=row["start_time"].strftime("%H:%M"),
            end_time=row["end_time"].strftime("%H:%M"),
            status=row["status"],
            room_name=row["room_name"],
            patient_name=row["patient_name"],
            doctor_name=row["doctor_name"],
            service_name=row["service_name"],
        )
        for row in rows
    ]

    return BookingSearchResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )

###---
# async def search_bookings_service(
#     db: AsyncSession,
#     *,
#     q: str | None,
#     company_code: str | None,
#     location_id: UUID | None,
#     booking_date: date | None,
#     page: int,
#     page_size: int,
# ) -> BookingSearchResponse:
#     offset = (page - 1) * page_size

#     # ✅ ใช้ค่าว่าง '' แทน None เพื่อหลบ AmbiguousParameterError
#     q_val = q or ""
#     company_code_val = company_code or ""
#     location_id_val = str(location_id) if location_id else ""
#     booking_date_val = booking_date.isoformat() if booking_date else ""

#     sql = text(
#         """
#         SELECT
#           b.id,
#           b.booking_date,
#           b.start_time,
#           b.end_time,
#           b.status,
#           r.room_name,
#           p.full_name_lo AS patient_name,
#           s.staff_name   AS doctor_name,
#           sv.service_name
#         FROM public.bookings b
#         LEFT JOIN public.rooms r    ON r.id  = b.room_id
#         LEFT JOIN public.patients p ON p.id  = b.patient_id
#         LEFT JOIN public.staff s    ON s.id  = b.primary_person_id
#         LEFT JOIN public.services sv ON sv.id = b.service_id
#         WHERE (:company_code = '' OR b.company_code = :company_code)
#           AND (:location_id = '' OR b.location_id::text = :location_id)
#           AND (:booking_date = '' OR b.booking_date::text = :booking_date)
#           AND (
#             :q = '' OR
#             p.full_name_lo  ILIKE '%' || :q || '%' OR
#             s.staff_name    ILIKE '%' || :q || '%' OR
#             sv.service_name ILIKE '%' || :q || '%'
#           )
#         ORDER BY b.booking_date DESC, b.start_time
#         LIMIT :limit OFFSET :offset;
#         """
#     )

#     count_sql = text(
#         """
#         SELECT count(*)
#         FROM public.bookings b
#         LEFT JOIN public.patients p ON p.id = b.patient_id
#         LEFT JOIN public.staff s    ON s.id = b.primary_person_id
#         LEFT JOIN public.services sv ON sv.id = b.service_id
#         WHERE (:company_code = '' OR b.company_code = :company_code)
#           AND (:location_id = '' OR b.location_id::text = :location_id)
#           AND (:booking_date = '' OR b.booking_date::text = :booking_date)
#           AND (
#             :q = '' OR
#             p.full_name_lo  ILIKE '%' || :q || '%' OR
#             s.staff_name    ILIKE '%' || :q || '%' OR
#             sv.service_name ILIKE '%' || :q || '%'
#           );
#         """
#     )

#     params = {
#         "q": q_val,
#         "company_code": company_code_val,
#         "location_id": location_id_val,
#         "booking_date": booking_date_val,
#         "limit": page_size,
#         "offset": offset,
#     }

#     rows = (await db.execute(sql, params)).mappings().all()
#     total = (await db.execute(count_sql, params)).scalar_one()

#     items = [
#         BookingListItem(
#             id=row["id"],
#             booking_date=row["booking_date"],
#             start_time=row["start_time"].strftime("%H:%M"),
#             end_time=row["end_time"].strftime("%H:%M"),
#             status=row["status"],
#             room_name=row["room_name"],
#             patient_name=row["patient_name"],
#             doctor_name=row["doctor_name"],
#             service_name=row["service_name"],
#         )
#         for row in rows
#     ]

#     return BookingSearchResponse(
#         items=items,
#         page=page,
#         page_size=page_size,
#         total=total,
#     )


#==================================



# ---------- Availability (simple sample) ----------

async def get_resource_availability_service(
    db: AsyncSession,
    *,
    resource_track_id: UUID,
    date_: date,
) -> AvailabilityResponse:
    # ตัวอย่างง่าย ๆ: สมมติว่าทำงานจาก 09:00–17:00 slot 30 min
    # ในโปรดักชันให้ใช้ tables: resource_track, resource_work_pattern, resource_track_block, bookings
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