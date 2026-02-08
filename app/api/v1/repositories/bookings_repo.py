# app/api/v1/repositories/bookings_repo.py
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from fastapi import HTTPException

from app.services.supabase_client import supabase


def _handle_supabase_error(res, context: str):
    err = getattr(res, "error", None)
    if not err:
        return

    # supabase-py error may be dict OR object
    if isinstance(err, dict):
        code = err.get("code")
        msg = err.get("message") or str(err)
        details = err.get("details")
    else:
        code = getattr(err, "code", None) or getattr(err, "error_code", None)
        msg = getattr(err, "message", None) or str(err)
        details = getattr(err, "details", None)

    # PostgREST .single() with 0 rows (or multiple) -> NOT_FOUND
    if code == "PGRST116":
        raise HTTPException(status_code=404, detail="NOT_FOUND")

    # PG constraint / invalid inputs -> INVALID
    pg_invalid = {"22P02", "22007"}                 # invalid uuid / invalid datetime
    pg_constraint = {"23503", "23514", "23505"}     # fk/check/unique
    if code in (pg_invalid | pg_constraint):
        raise HTTPException(
            status_code=422,
            detail=f"INVALID:{code}:{msg}",
        )

    # default -> 500
    raise HTTPException(status_code=500, detail=f"{context}: ({code}) {msg} {details or ''}".strip())


# ==========================================================
# Repo: create / read / update / delete (table: bookings)
# ==========================================================
def repo_insert_booking(payload: dict[str, Any]) -> dict[str, Any]:
    res = supabase.table("bookings").insert(payload).execute()
    _handle_supabase_error(res, "repo_insert_booking")
    if not res.data:
        raise HTTPException(status_code=500, detail="repo_insert_booking: no data returned")
    return res.data[0]


def repo_select_booking_row(booking_id: UUID, fields: str = "id,status,updated_at") -> Optional[dict[str, Any]]:
    res = supabase.table("bookings").select(fields).eq("id", str(booking_id)).single().execute()
    _handle_supabase_error(res, "repo_select_booking_row")
    return res.data or None


def repo_update_booking(booking_id: UUID, payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    upd = supabase.table("bookings").update(payload).eq("id", str(booking_id)).execute()
    _handle_supabase_error(upd, "repo_update_booking")

    # re-select (to return latest)
    return repo_select_booking_row(booking_id, fields="id,status,updated_at")


def repo_delete_booking(booking_id: UUID) -> bool:
    res = supabase.table("bookings").delete().eq("id", str(booking_id)).execute()
    _handle_supabase_error(res, "repo_delete_booking")
    return True


# ==========================================================
# Repo: booking grid view (view: booking_grid_view)
# ==========================================================
def repo_get_booking_detail_from_grid_view(booking_id: UUID) -> Optional[dict[str, Any]]:
    res = (
        supabase.table("booking_grid_view")
        .select(
            "booking_id,company_code,location_id,building_id,room_id,room_name,"
            "patient_id,patient_name,patient_telephone,doctor_id,doctor_name,"
            "service_id,service_name,booking_date,start_time,end_time,status,source_of_ad,note"
        )
        .eq("booking_id", str(booking_id))
        .limit(1)
        .execute()
    )
    _handle_supabase_error(res, "repo_get_booking_detail_from_grid_view")

    rows = res.data or []
    return rows[0] if rows else None


def repo_search_booking_grid_view(
    *,
    q: Optional[str],
    company_code: Optional[str],
    location_id: Optional[UUID],
    booking_date: Optional[str],
    limit: int,
    offset: int,
) -> tuple[int, list[dict[str, Any]]]:
    """
    Returns (total_exact, page_rows)
    Uses: count="exact" + range(offset, offset+limit-1)
    """
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
        query = query.eq("booking_date", booking_date)

    if q:
        query = query.or_(
            f"patient_name.ilike.%{q}%,doctor_name.ilike.%{q}%,service_name.ilike.%{q}%,room_name.ilike.%{q}%"
        )

    query = (
        query.order("booking_date", desc=True)
        .order("start_time", desc=False)
        .order("room_name", desc=False)
        .order("booking_id", desc=False)
    )

    res = query.range(offset, offset + limit - 1).execute()
    _handle_supabase_error(res, "repo_search_booking_grid_view")

    total = int(getattr(res, "count", 0) or 0)
    rows = res.data or []
    return total, rows


# ==========================================================
# Repo: history (table: booking_status_history)
# ==========================================================
def repo_insert_status_history(payload: dict[str, Any]) -> None:
    res = supabase.table("booking_status_history").insert(payload).execute()
    _handle_supabase_error(res, "repo_insert_status_history")


def repo_get_status_history(booking_id: UUID) -> list[dict[str, Any]]:
    res = (
        supabase.table("booking_status_history")
        .select("id,old_status,new_status,changed_at,changed_by,note")
        .eq("booking_id", str(booking_id))
        .order("changed_at", desc=True)
        .execute()
    )
    _handle_supabase_error(res, "repo_get_status_history")
    return res.data or []
