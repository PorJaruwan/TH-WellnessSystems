# app/api/v1/services/bookings_service.py
from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Optional, Union
from uuid import UUID
from enum import Enum

from fastapi import HTTPException

from app.api.v1.models.bookings_model import (
    BookingCreate,
    BookingCreateResponse,
    BookingDetail,
    BookingHistoryItem,
    BookingListItem,
    BookingUpdateResponse,
    BookingActionEnum,  # ✅ ADD
)


from app.api.v1.repositories.bookings_repo import (
    repo_delete_booking,
    repo_get_booking_detail_from_grid_view,
    repo_get_status_history,
    repo_insert_booking,
    repo_insert_status_history,
    repo_search_booking_grid_view,
    repo_select_booking_row,
    repo_update_booking,
)


# ---------- Helpers ----------
def _parse_time_flexible(t: Union[str, time]) -> time:
    if isinstance(t, time):
        return t
    if not t or not isinstance(t, str):
        raise HTTPException(status_code=422, detail="INVALID:start_time/end_time must be a time or string")

    tt = t.strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(tt, fmt).time()
        except ValueError:
            pass

    raise HTTPException(
        status_code=422,
        detail="INVALID:start_time and end_time must be in 'HH:MM' or 'HH:MM:SS' format",
    )


def _coerce_empty_str(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    vv = v.strip()
    return vv if vv else None


def _coerce_booking_date(d: Union[date, str, None]) -> Optional[str]:
    if d is None:
        return None
    if isinstance(d, date):
        return d.isoformat()
    if isinstance(d, str):
        dd = d.strip()
        if not dd:
            return None
        try:
            return date.fromisoformat(dd).isoformat()
        except ValueError:
            raise HTTPException(status_code=422, detail="INVALID:booking_date must be 'YYYY-MM-DD'")
    raise HTTPException(status_code=422, detail="INVALID:booking_date must be a date or 'YYYY-MM-DD' string")


def _jsonify_value(v):
    if v is None:
        return None
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, UUID):
        return str(v)
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, time):
        return v.isoformat()
    return v

def _jsonify_payload(payload: dict) -> dict:
    return {k: _jsonify_value(v) for k, v in payload.items()}

def _enum_value(v):
    return v.value if hasattr(v, "value") else v


def _utc_now_iso() -> str:
    """UTC now in ISO 8601 with timezone."""
    return datetime.now(timezone.utc).isoformat()


def _to_iso_utc(v) -> Optional[str]:
    """
    Convert datetime/ISO-string to ISO 8601 UTC string.
    If parsing fails, fallback to str(v).
    """
    if v is None:
        return None

    if isinstance(v, datetime):
        # ensure UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc).isoformat()

    if isinstance(v, str):
        s = v.strip()
        # support Z
        s2 = s.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s2)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            return s

    return str(v)


# ==========================================================
# Service: Create / Read / Update / Delete
# ==========================================================
async def create_booking_service(body: BookingCreate) -> BookingCreateResponse:
    start_t = _parse_time_flexible(body.start_time)
    end_t = _parse_time_flexible(body.end_time)
    if end_t <= start_t:
        raise HTTPException(status_code=422, detail="INVALID:end_time must be after start_time")

    now = datetime.utcnow().isoformat()

    payload = {
        "resource_track_id": (str(body.resource_track_id) if body.resource_track_id else None),
        "company_code": body.company_code,
        "location_id": str(body.location_id),
        "building_id": str(body.building_id),
        "room_id": str(body.room_id),
        "patient_id": str(body.patient_id),
        "primary_person_id": str(body.primary_person_id),
        "service_id": str(body.service_id),
        "booking_date": body.booking_date.isoformat(),
        "start_time": start_t.isoformat(),
        "end_time": end_t.isoformat(),
        "source_of_ad": _enum_value(body.source_of_ad) if body.source_of_ad else None,
        "note": body.note,
        "cancel_reason": body.cancel_reason,
        "status": _enum_value(body.status) or "booked",
        "created_at": now,
        "updated_at": now,
    }

    row = repo_insert_booking(payload)
    return BookingCreateResponse(id=row["id"], status=row.get("status", payload["status"]))


async def get_booking_detail_service(*, booking_id: UUID) -> BookingDetail:
    row = repo_get_booking_detail_from_grid_view(booking_id)
    if not row:
        raise HTTPException(status_code=404, detail="NOT_FOUND")

    # view returns booking_id
    start_iso = row["start_time"]
    end_iso = row["end_time"]

    # convert to HH:MM
    start_hhmm = time.fromisoformat(start_iso).strftime("%H:%M") if isinstance(start_iso, str) else str(start_iso)
    end_hhmm = time.fromisoformat(end_iso).strftime("%H:%M") if isinstance(end_iso, str) else str(end_iso)

    booking_date_val = row["booking_date"]
    booking_date_obj = date.fromisoformat(booking_date_val) if isinstance(booking_date_val, str) else booking_date_val

    return BookingDetail(
        id=row["booking_id"],
        company_code=row["company_code"],
        location_id=row["location_id"],
        building_id=row["building_id"],
        booking_date=booking_date_obj,
        start_time=start_hhmm,
        end_time=end_hhmm,
        status=row["status"],
        room_id=row["room_id"],
        room_name=row.get("room_name") or "",
        patient_id=row["patient_id"],
        patient_name=row.get("patient_name") or "",
        patient_telephone=row.get("patient_telephone"),
        doctor_id=row["doctor_id"],
        doctor_name=row.get("doctor_name") or "",
        service_id=row["service_id"],
        service_name=row.get("service_name") or "",
        source_of_ad=row.get("source_of_ad"),
        note=row.get("note"),
    )


async def update_booking_by_id_service(*, booking_id: UUID, payload: dict) -> BookingUpdateResponse:
    if not payload or not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="INVALID:payload must be a non-empty JSON object")

    clean = _jsonify_payload(dict(payload))

    # normalize empty strings -> None for nullable text
    for k in ("note", "cancel_reason", "source_of_ad"):
        if k in clean and isinstance(clean[k], str) and clean[k].strip() == "":
            clean[k] = None

    clean["updated_at"] = datetime.utcnow().isoformat()

    updated = repo_update_booking(booking_id, clean)
    if not updated:
        raise HTTPException(status_code=404, detail="NOT_FOUND")

    # repo_select_booking_row returns minimal fields
    return BookingUpdateResponse(
        id=UUID(str(updated["id"])),
        status=updated.get("status"),
        updated_at=str(updated.get("updated_at")) if updated.get("updated_at") is not None else None,
    )


async def delete_booking_service(*, booking_id: UUID) -> None:
    exists = repo_select_booking_row(booking_id, fields="id")
    if not exists:
        raise HTTPException(status_code=404, detail="NOT_FOUND")

    repo_delete_booking(booking_id)


# ==========================================================
# Service: Search (limit/offset + exact count)
# ==========================================================
async def search_bookings_service(
    *,
    q: Optional[str],
    company_code: Optional[str],
    location_id: Optional[UUID],
    booking_date: Union[date, str, None],
    limit: int,
    offset: int,
) -> tuple[int, list[BookingListItem]]:
    q = _coerce_empty_str(q)
    company_code = _coerce_empty_str(company_code)
    booking_date_iso = _coerce_booking_date(booking_date)

    total, rows = repo_search_booking_grid_view(
        q=q,
        company_code=company_code,
        location_id=location_id,
        booking_date=booking_date_iso,
        limit=limit,
        offset=offset,
    )

    items: list[BookingListItem] = []
    for r in rows:
        items.append(
            BookingListItem(
                id=r["booking_id"],
                booking_date=r["booking_date"] if isinstance(r["booking_date"], date) else date.fromisoformat(r["booking_date"]),
                start_time=str(r.get("start_time") or ""),
                end_time=str(r.get("end_time") or ""),
                status=str(r.get("status") or ""),
                room_name=str(r.get("room_name") or ""),
                patient_name=str(r.get("patient_name") or ""),
                doctor_name=str(r.get("doctor_name") or ""),
                service_name=str(r.get("service_name") or ""),
            )
        )

    return total, items


# ==========================================================
# Service: Status Action + History
# ==========================================================
async def booking_status_action_service(
    *,
    booking_id: UUID,
    user_id: UUID,
    action: str | BookingActionEnum,
    note: Optional[str] = None,
    cancel_reason: Optional[str] = None,
    force: bool = False,
) -> dict:
    # --- normalize (support Enum or str) ---
    action_key = action.value if hasattr(action, "value") else (str(action or "").strip().lower())

    # --- strict allowed actions (single source of truth) ---
    new_status_map = {
        "confirm": "confirmed",
        "checkin": "checked_in",
        "start_service": "in_service",
        "complete": "completed",
        "cancel": "cancelled",
        "no_show": "no_show",
        "reschedule": "rescheduled",
    }
    allowed_actions = sorted(new_status_map.keys())

    if action_key not in new_status_map:
        raise HTTPException(
            status_code=422,
            detail=f"INVALID:action must be one of {allowed_actions}",
        )

    # --- defense-in-depth (model already validates, but keep service strict) ---
    note_clean = _coerce_empty_str(note)
    cancel_reason_clean = _coerce_empty_str(cancel_reason)

    if action_key == "cancel" and not cancel_reason_clean:
        raise HTTPException(status_code=422, detail="INVALID:cancel_reason is required when action='cancel'")

    if action_key != "cancel" and cancel_reason_clean:
        raise HTTPException(status_code=422, detail="INVALID:cancel_reason is only allowed when action='cancel'")

    # --- load booking ---
    row = repo_select_booking_row(booking_id, fields="id,status")
    if not row:
        raise HTTPException(status_code=404, detail="NOT_FOUND")

    old_status = row.get("status")
    new_status = new_status_map[action_key]

    # --- no-op if same status (unless force) ---
    if (not force) and old_status == new_status:
        return {"booking_id": str(booking_id), "old_status": old_status, "status": new_status}

    # --- update status ---
    updated = repo_update_booking(
        booking_id,
        {"status": new_status, "updated_at": _utc_now_iso()},
    )

    if not updated:
        raise HTTPException(status_code=404, detail="NOT_FOUND")

    # --- history note policy (keep behavior, but cleaner) ---
    history_note = note_clean or (cancel_reason_clean if action_key == "cancel" else None)

    repo_insert_status_history(
        {
            "booking_id": str(booking_id),
            "old_status": old_status,
            "new_status": new_status,
            "changed_by": str(user_id),
            "note": history_note,
        }
    )

    return {
        "booking_id": str(updated.get("id") or booking_id),
        "old_status": old_status,
        "status": updated.get("status") or new_status,
        "updated_at": _to_iso_utc(updated.get("updated_at")),  # ISO 8601 + UTC
    }


# async def booking_status_action_service(
#     *,
#     booking_id: UUID,
#     user_id: UUID,
#     action: str,
#     note: Optional[str] = None,
#     cancel_reason: Optional[str] = None,
#     force: bool = False,
# ) -> dict:
#     allowed = {"confirm", "checkin", "start_service", "complete", "cancel", "no_show", "reschedule"}
#     if action not in allowed:
#         raise HTTPException(status_code=422, detail="INVALID:action")

#     row = repo_select_booking_row(booking_id, fields="id,status")
#     if not row:
#         raise HTTPException(status_code=404, detail="NOT_FOUND")

#     old_status = row.get("status")
#     new_status_map = {
#         "confirm": "confirmed",
#         "checkin": "checked_in",
#         "start_service": "in_service",
#         "complete": "completed",
#         "cancel": "cancelled",
#         "no_show": "no_show",
#         "reschedule": "rescheduled",
#     }
#     new_status = new_status_map[action]

#     if (not force) and old_status == new_status:
#         return {"booking_id": str(booking_id), "old_status": old_status, "status": new_status, "updated_at": None}


#     updated = repo_update_booking(
#         booking_id,
#         {"status": new_status, "updated_at": datetime.utcnow().isoformat()},
#     )
#     if not updated:
#         raise HTTPException(status_code=404, detail="NOT_FOUND")

#     repo_insert_status_history(
#         {
#             "booking_id": str(booking_id),
#             "old_status": old_status,
#             "new_status": new_status,
#             "changed_by": str(user_id),
#             "note": note or (cancel_reason if action == "cancel" else None),
#         }
#     )

#     return {
#         "id": updated["id"],
#         "old_status": old_status,
#         "status": updated.get("status"),
#         "updated_at": str(updated.get("updated_at")) if updated.get("updated_at") is not None else None,
#     }


async def get_booking_history_service(*, booking_id: UUID) -> list[BookingHistoryItem]:
    rows = repo_get_status_history(booking_id)
    items: list[BookingHistoryItem] = []

    for r in rows:
        changed_at = r.get("changed_at")
        items.append(
            BookingHistoryItem(
                id=r["id"],
                old_status=r.get("old_status"),
                new_status=r["new_status"],
                changed_at=(
                    datetime.fromisoformat(changed_at).isoformat()
                    if isinstance(changed_at, str)
                    else str(changed_at)
                ),
                changed_by=r.get("changed_by"),
                note=r.get("note"),
            )
        )
    return items
