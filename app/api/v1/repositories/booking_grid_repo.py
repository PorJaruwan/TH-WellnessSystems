# app/api/v1/repositories/booking_grid_repo.py

from __future__ import annotations
from typing import Any, Optional
from uuid import UUID
from fastapi import HTTPException
from app.services.supabase_client import supabase


def _handle_supabase_error(res, context: str):
    err = getattr(res, "error", None)
    if not err:
        return

    if isinstance(err, dict):
        code = err.get("code")
        msg = err.get("message") or str(err)
        details = err.get("details")
    else:
        code = getattr(err, "code", None) or getattr(err, "error_code", None)
        msg = getattr(err, "message", None) or str(err)
        details = getattr(err, "details", None)

    # ---- NOT_FOUND (single() but 0 rows) ----
    if code == "PGRST116":
        raise HTTPException(status_code=404, detail="NOT_FOUND")

    # ---- INVALID ----
    pg_invalid = {"22P02", "22007"}                 # invalid uuid / invalid date-time
    pg_constraint = {"23503", "23514", "23505"}     # fk/check/unique
    if code in (pg_invalid | pg_constraint):
        raise HTTPException(status_code=422, detail=f"INVALID:{code}:{msg}")

    # ---- default -> 500 ----
    raise HTTPException(status_code=500, detail=f"{context}: ({code}) {msg} {details or ''}".strip())



# ==========================================================
# Repo: booking_view_config (max_columns)
# ==========================================================
def repo_get_max_columns(*, company_code: str, location_id: UUID, building_id: UUID) -> Optional[int]:
    res = (
        supabase.table("booking_view_config")
        .select("max_columns")
        .eq("company_code", company_code)
        .eq("location_id", str(location_id))
        .eq("building_id", str(building_id))
        .eq("is_active", True)
        .order("is_default", desc=True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    _handle_supabase_error(res, "repo_get_max_columns")

    row = (res.data or [None])[0]
    if not row:
        return None
    v = row.get("max_columns")
    try:
        return int(v) if v is not None else None
    except Exception:
        return None


# ==========================================================
# Repo: booking_timeslot_exception (date-based override)
# ==========================================================
def repo_get_timeslot_exception(
    *,
    company_code: str,
    location_id: UUID,
    building_id: UUID,
    booking_date_iso: str,
) -> Optional[dict[str, Any]]:
    # NOTE: many designs use column name "date" for exception table
    res = (
        supabase.table("booking_timeslot_exception")
        .select("time_from,time_to,slot_min,is_closed")
        .eq("company_code", company_code)
        .eq("location_id", str(location_id))
        .eq("building_id", str(building_id))
        .eq("date", booking_date_iso)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    _handle_supabase_error(res, "repo_get_timeslot_exception")
    return (res.data or [None])[0]


# ==========================================================
# Repo: booking_timeslot_config (default)
# ==========================================================
def repo_get_timeslot_config(*, company_code: str, location_id: UUID, building_id: UUID) -> Optional[dict[str, Any]]:
    res = (
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
    _handle_supabase_error(res, "repo_get_timeslot_config")
    return (res.data or [None])[0]


# ==========================================================
# Repo: rooms for building
# ==========================================================
def repo_get_rooms_for_building(*, building_id: UUID) -> list[dict[str, Any]]:
    res = (
        supabase.table("rooms")
        .select("id,room_name")
        .eq("building_id", str(building_id))
        .eq("is_active", True)
        .order("room_name", desc=False)
        .execute()
    )
    _handle_supabase_error(res, "repo_get_rooms_for_building")
    return res.data or []


# ==========================================================
# Repo: bookings from booking_grid_view (filtered)
# ==========================================================
def repo_get_booking_grid_rows(
    *,
    company_code: str,
    location_id: UUID,
    building_id: UUID,
    booking_date_iso: str,
    room_ids: list[UUID] | None = None,
) -> list[dict[str, Any]]:
    q = (
        supabase.table("booking_grid_view")
        .select("booking_id,room_id,start_time,end_time,status,patient_name,doctor_name,service_name")
        .eq("company_code", company_code)
        .eq("location_id", str(location_id))
        .eq("building_id", str(building_id))
        .eq("booking_date", booking_date_iso)
    )

    # ✅ FIX: supabase-py in_ ต้องส่ง list ไม่ต้องส่ง "(...)" string
    if room_ids:
        q = q.in_("room_id", [str(x) for x in room_ids])

    res = q.execute()
    _handle_supabase_error(res, "repo_get_booking_grid_rows")
    return res.data or []
