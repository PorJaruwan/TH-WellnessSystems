# app/api/v1/services/booking_grid_service.py

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Dict, List, Literal, Optional
from uuid import UUID

from fastapi import HTTPException

from app.api.v1.models.booking_grid_model import (
    BookingGridAny,
    BookingGridCell,
    BookingGridColumn,
    BookingGridColumnsPayload,
    BookingGridColumnsRow,
    BookingGridFlatItem,
    BookingGridFlatPayload,
    BookingGridGridPayload,
    BookingGridRoom,
    BookingGridSlot,
    BookingGridTimeRow,
)

from app.api.v1.repositories.booking_grid_repo import (
    repo_get_booking_grid_rows,
    repo_get_max_columns,
    repo_get_rooms_for_building,
    repo_get_timeslot_config,
    repo_get_timeslot_exception,
)

GridFormat = Literal["grid", "flat", "columns"]
ViewMode = Literal["full", "am", "pm"]


# ---------------- Helpers ----------------
def _time_range(start: time, end: time, slot_min: int) -> List[time]:
    times: List[time] = []
    cur = datetime.combine(date.today(), start)
    end_dt = datetime.combine(date.today(), end)
    step = timedelta(minutes=slot_min)
    while cur < end_dt:
        times.append(cur.time())
        cur += step
    return times


def _fmt_hhmm(t: time) -> str:
    return t.strftime("%H:%M")


def _status_label(status: str) -> str:
    s = (status or "").strip().lower()
    return {
        "draft": "Draft",
        "booked": "Booked",
        "confirmed": "Confirmed",
        "checked_in": "Checked-in",
        "in_service": "In Service",
        "completed": "Completed",
        "no_show": "No Show",
        "cancelled": "Cancelled",
        "available": "Available",
        "locked": "Locked",
        "closed": "Closed",
    }.get(s, s.replace("_", " ").title())


def _coerce_int(v: Optional[int], default: int) -> int:
    try:
        return int(v) if v is not None else default
    except Exception:
        return default


# ==========================================================
# Service: Compose grid payload (type-safe model)
# Raises:
#   - 404 detail "EMPTY:*" => router maps to EMPTY
#   - 404 normal => NOT_FOUND
#   - 422 => INVALID
# ==========================================================
async def get_booking_grid_service(
    *,
    booking_date: date,
    company_code: str,
    location_id: UUID,
    building_id: UUID,
    view_mode: ViewMode = "full",
    page: int = 1,
    format: GridFormat = "grid",
    columns: int | None = None,
) -> BookingGridAny:
    booking_date_iso = booking_date.isoformat()

    # 1) columns per page
    max_cols_cfg = repo_get_max_columns(company_code=company_code, location_id=location_id, building_id=building_id)
    max_columns = _coerce_int(max_cols_cfg, 5)
    if columns is not None:
        max_columns = int(columns)

    if max_columns <= 0:
        raise HTTPException(status_code=422, detail="columns must be >= 1")

    # 2) timeslot exception (per date)
    exc = repo_get_timeslot_exception(
        company_code=company_code,
        location_id=location_id,
        building_id=building_id,
        booking_date_iso=booking_date_iso,
    )
    if exc and exc.get("is_closed") is True:
        raise HTTPException(status_code=404, detail="EMPTY:CLOSED")

    # 3) time window + slot_min
    if exc and exc.get("time_from") and exc.get("time_to"):
        time_from = time.fromisoformat(exc["time_from"])
        time_to = time.fromisoformat(exc["time_to"])
        slot_min = int(exc.get("slot_min") or 30)
    else:
        cfg = repo_get_timeslot_config(company_code=company_code, location_id=location_id, building_id=building_id)
        if cfg:
            time_from = time.fromisoformat(cfg["time_from"])
            time_to = time.fromisoformat(cfg["time_to"])
            slot_min = int(cfg.get("slot_min") or 30)
        else:
            # fallback default
            time_from = time(9, 0)
            time_to = time(17, 0)
            slot_min = 30

    if slot_min <= 0:
        raise HTTPException(status_code=422, detail="slot_min must be >= 1")

    # 4) view_mode slicing
    if view_mode in ("am", "pm"):
        start_dt = datetime.combine(date.today(), time_from)
        end_dt = datetime.combine(date.today(), time_to)
        if end_dt <= start_dt:
            raise HTTPException(status_code=422, detail="Invalid time window")
        mid_dt = start_dt + (end_dt - start_dt) / 2
        mid = mid_dt.time()
        if view_mode == "am":
            time_to = mid
        else:
            time_from = mid

    # 5) rooms (paginate by columns)
    all_rooms = repo_get_rooms_for_building(building_id=building_id)
    if not all_rooms:
        raise HTTPException(status_code=404, detail="EMPTY:NO_ROOMS")

    total_rooms = len(all_rooms)
    total_pages = (total_rooms + max_columns - 1) // max_columns or 1
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * max_columns
    end_idx = start_idx + max_columns
    rooms_slice = all_rooms[start_idx:end_idx]

    rooms_out = [BookingGridRoom(room_id=UUID(r["id"]) if isinstance(r["id"], str) else r["id"], room_name=r["room_name"]) for r in rooms_slice]
    visible_room_ids = [r.room_id for r in rooms_out]

    # 6) bookings for visible rooms from view
    rows = repo_get_booking_grid_rows(
        company_code=company_code,
        location_id=location_id,
        building_id=building_id,
        booking_date_iso=booking_date_iso,
        room_ids=visible_room_ids,
    )

    # map bookings into slots
    step = timedelta(minutes=slot_min)
    booking_map: Dict[tuple[str, time], dict] = {}

    for row in rows:
        room_id = str(row["room_id"])
        start_t = time.fromisoformat(row["start_time"])
        end_t = time.fromisoformat(row["end_time"])

        cur = datetime.combine(date.today(), start_t)
        end_dt = datetime.combine(date.today(), end_t)
        while cur < end_dt:
            booking_map[(room_id, cur.time())] = row
            cur += step

    time_points = _time_range(time_from, time_to, slot_min)

    # -------- format = columns --------
    if format == "columns":
        columns_meta = [BookingGridColumn(col=i, room_id=r.room_id, room_name=r.room_name) for i, r in enumerate(rooms_out, start=1)]

        rows_out: list[BookingGridColumnsRow] = []
        for t in time_points:
            row_dict: dict = {"time": _fmt_hhmm(t)}
            for i, r in enumerate(rooms_out, start=1):
                key = f"col{i}"
                b = booking_map.get((str(r.room_id), t))
                if b:
                    st = b["status"]
                    row_dict[key] = BookingGridCell(
                        room_id=r.room_id,
                        status=st,
                        status_label=_status_label(st),
                        booking_id=b.get("booking_id"),
                        patient_name=b.get("patient_name"),
                        doctor_name=b.get("doctor_name"),
                        service_name=b.get("service_name"),
                    ).model_dump(exclude_none=True)
                else:
                    row_dict[key] = BookingGridCell(
                        room_id=r.room_id,
                        status="available",
                        status_label=_status_label("available"),
                    ).model_dump(exclude_none=True)

            rows_out.append(BookingGridColumnsRow(**row_dict))

        return BookingGridColumnsPayload(
            date=booking_date,
            time_from=_fmt_hhmm(time_from),
            time_to=_fmt_hhmm(time_to),
            slot_min=slot_min,
            page=page,
            total_pages=total_pages,
            columns=columns_meta,
            rows=rows_out,
        )

    # -------- format = grid --------
    if format == "grid":
        time_rows: list[BookingGridTimeRow] = []
        for t in time_points:
            slots: list[BookingGridSlot] = []
            for r in rooms_out:
                b = booking_map.get((str(r.room_id), t))
                if b:
                    st = b["status"]
                    slots.append(
                        BookingGridSlot(
                            room_id=r.room_id,
                            status=st,
                            status_label=_status_label(st),
                            booking_id=b.get("booking_id"),
                            patient_name=b.get("patient_name"),
                            doctor_name=b.get("doctor_name"),
                            service_name=b.get("service_name"),
                        )
                    )
                else:
                    slots.append(
                        BookingGridSlot(
                            room_id=r.room_id,
                            status="available",
                            status_label=_status_label("available"),
                        )
                    )
            time_rows.append(BookingGridTimeRow(time=_fmt_hhmm(t), slots=slots))

        return BookingGridGridPayload(
            date=booking_date,
            time_from=_fmt_hhmm(time_from),
            time_to=_fmt_hhmm(time_to),
            slot_min=slot_min,
            rooms=rooms_out,
            timeslots=time_rows,
            page=page,
            total_pages=total_pages,
        )

    # -------- format = flat --------
    if format == "flat":
        items: list[BookingGridFlatItem] = []
        for t in time_points:
            t_str = _fmt_hhmm(t)
            for r in rooms_out:
                b = booking_map.get((str(r.room_id), t))
                if b:
                    st = b["status"]
                    items.append(
                        BookingGridFlatItem(
                            time=t_str,
                            room_id=r.room_id,
                            room_name=r.room_name,
                            status=st,
                            status_label=_status_label(st),
                            booking_id=b.get("booking_id"),
                            patient_name=b.get("patient_name"),
                            doctor_name=b.get("doctor_name"),
                            service_name=b.get("service_name"),
                        )
                    )
                else:
                    items.append(
                        BookingGridFlatItem(
                            time=t_str,
                            room_id=r.room_id,
                            room_name=r.room_name,
                            status="available",
                            status_label=_status_label("available"),
                        )
                    )

        return BookingGridFlatPayload(
            date=booking_date,
            time_from=_fmt_hhmm(time_from),
            time_to=_fmt_hhmm(time_to),
            slot_min=slot_min,
            rooms=rooms_out,
            page=page,
            total_pages=total_pages,
            total=len(items),
            items=items,
        )

    # should not reach (router validates), but keep safe
    raise HTTPException(status_code=422, detail="Invalid format")
