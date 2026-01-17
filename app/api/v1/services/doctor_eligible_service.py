# app/services/doctor_eligible_service.py
"""
Doctor search service (Requirement 1–4)

Requirement mapping:
R1: Eligible doctors by room (+ optional location)
R2: Eligible + working day (staff_work_pattern) + not on leave (staff_leave)  [optional via check_timeslot]
R3: Eligible + not conflict with bookings                               [optional via check_booking]
R4: All checks are optional via flags: check_location/check_timeslot/check_booking

Inputs:
- room_id (uuid)
- location_id (uuid | None)
- role (str)
- date (date | None)
- time (time | None)
- check_location (bool)
- check_timeslot (bool)
- check_booking (bool)

DB:
- SQLAlchemy AsyncSession (project uses create_async_engine + AsyncSessionLocal via get_db)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as date_type, time as time_type
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# ----------------------------
# Helpers
# ----------------------------

def weekday_0_sun(d: date_type) -> int:
    """
    Convert Python weekday (Mon=0..Sun=6) -> DB weekday (Sun=0..Sat=6)
    """
    return (d.weekday() + 1) % 7


@dataclass(frozen=True)
class DoctorSearchParams:
    room_id: UUID
    role: str = "doctor"

    # optional context
    location_id: Optional[UUID] = None
    date: Optional[date_type] = None
    time: Optional[time_type] = None

    # optional checks
    check_location: bool = False
    check_timeslot: bool = False
    check_booking: bool = False

    def validate(self) -> None:
        if self.check_location and self.location_id is None:
            raise ValueError("check_location=true requires location_id")

        if (self.check_timeslot or self.check_booking) and (self.date is None or self.time is None):
            raise ValueError("check_timeslot/check_booking requires both date and time")


# ----------------------------
# SQL (single query, optional flags)
# ----------------------------

SQL_ELIGIBLE_DOCTORS = text(
    """
WITH room_ctx AS (
  SELECT r.id AS room_id, r.location_id
  FROM public.rooms r
  WHERE r.id = :room_id
),
staff_base AS (
  SELECT st.id AS staff_id, st.staff_name, st.role, rc.location_id
  FROM room_ctx rc
  JOIN public.staff_locations sl
    ON sl.location_id = rc.location_id
   AND sl.is_active = TRUE
  JOIN public.staff st
    ON st.id = sl.staff_id
   AND st.is_active = TRUE
   AND st.role = :role
  WHERE
    (:check_location = FALSE)
    OR (rc.location_id = :location_id)
),
eligible_by_service AS (
  SELECT
    sb.staff_id,
    sb.staff_name,
    sb.role,
    sb.location_id,
    COUNT(DISTINCT rs.service_id) AS matched_service_count,
    ARRAY_AGG(DISTINCT rs.service_id ORDER BY rs.service_id) AS matched_service_ids
  FROM staff_base sb
  JOIN room_ctx rc ON rc.location_id = sb.location_id
  JOIN public.room_services rs
    ON rs.room_id = rc.room_id
   AND rs.is_active = TRUE
  JOIN public.staff_services ss
    ON ss.staff_id = sb.staff_id
   AND ss.service_id = rs.service_id
   AND ss.is_active = TRUE
  GROUP BY sb.staff_id, sb.staff_name, sb.role, sb.location_id
  HAVING COUNT(DISTINCT rs.service_id) > 0
),
filtered_timeslot AS (
  SELECT e.*
  FROM eligible_by_service e
  WHERE
    (:check_timeslot = FALSE)
    OR (
      EXISTS (
        SELECT 1
        FROM public.staff_work_pattern wp
        WHERE wp.staff_id = e.staff_id
          AND wp.location_id = e.location_id
          AND wp.is_active = TRUE
          AND wp.weekday = :weekday
          AND (wp.valid_from IS NULL OR wp.valid_from <= :date)
          AND (wp.valid_to   IS NULL OR wp.valid_to   >= :date)
      )
      AND NOT EXISTS (
        SELECT 1
        FROM public.staff_leave lv
        WHERE lv.staff_id = e.staff_id
          AND lv.location_id = e.location_id
          AND lv.is_active = TRUE
          AND lv.status = 'approved'
          AND :date BETWEEN lv.date_from AND lv.date_to
          AND (
            lv.part_of_day IS NULL
            OR lv.part_of_day = 'full'
            OR (lv.part_of_day = 'morning'   AND :time <  TIME '12:00')
            OR (lv.part_of_day = 'afternoon' AND :time >= TIME '12:00')
          )
      )
    )
),
filtered_booking AS (
  SELECT t.*
  FROM filtered_timeslot t
  WHERE
    (:check_booking = FALSE)
    OR NOT EXISTS (
      SELECT 1
      FROM public.bookings b
      WHERE b.primary_person_id = t.staff_id
        AND b.booking_date = :date
        AND b.status <> 'cancelled'
        AND (:time >= b.start_time AND :time < b.end_time)
    )
)
SELECT
  staff_id,
  staff_name,
  role,
  location_id,
  matched_service_count,
  matched_service_ids
FROM filtered_booking
ORDER BY staff_name;
"""
)


# ----------------------------
# Public API
# ----------------------------

async def search_doctors_for_booking(
    db: AsyncSession,
    p: DoctorSearchParams,
) -> List[Dict[str, Any]]:
    """
    Returns list of eligible doctors for booking based on Requirement 1–4.

    Output keys:
      - staff_id (uuid)
      - staff_name (text)
      - role (text)
      - location_id (uuid)
      - matched_service_count (int)
      - matched_service_ids (uuid[])
    """
    p.validate()

    # weekday only required when check_timeslot=true, but safe to compute if date present
    weekday = weekday_0_sun(p.date) if p.date else 0

    params: Dict[str, Any] = {
        "room_id": str(p.room_id),
        "role": p.role,

        # optional values (SQL will ignore when flags are false)
        "location_id": str(p.location_id) if p.location_id else None,
        "date": p.date,
        "time": p.time,
        "weekday": weekday,

        # flags
        "check_location": p.check_location,
        "check_timeslot": p.check_timeslot,
        "check_booking": p.check_booking,
    }

    result = await db.execute(SQL_ELIGIBLE_DOCTORS, params)
    # mappings() -> rows as dict-like objects; convert to real dict for JSON response
    rows = [dict(r) for r in result.mappings().all()]
    return rows


# ----------------------------
# Convenience wrappers (optional)
# ----------------------------

async def search_doctors_r1(
    db: AsyncSession,
    room_id: UUID,
    role: str = "doctor",
) -> List[Dict[str, Any]]:
    """R1 only (eligible by room + role)."""
    p = DoctorSearchParams(
        room_id=room_id,
        role=role,
        check_location=False,
        check_timeslot=False,
        check_booking=False,
    )
    return await search_doctors_for_booking(db, p)


async def search_doctors_r1_location(
    db: AsyncSession,
    room_id: UUID,
    location_id: UUID,
    role: str = "doctor",
) -> List[Dict[str, Any]]:
    """R1 + check_location."""
    p = DoctorSearchParams(
        room_id=room_id,
        location_id=location_id,
        role=role,
        check_location=True,
        check_timeslot=False,
        check_booking=False,
    )
    return await search_doctors_for_booking(db, p)


async def search_doctors_r2_timeslot(
    db: AsyncSession,
    room_id: UUID,
    date: date_type,
    time: time_type,
    role: str = "doctor",
    location_id: Optional[UUID] = None,
    check_location: bool = False,
) -> List[Dict[str, Any]]:
    """R1 (+ optional location) + R2 timeslot (work_pattern + leave)."""
    p = DoctorSearchParams(
        room_id=room_id,
        location_id=location_id,
        role=role,
        date=date,
        time=time,
        check_location=check_location,
        check_timeslot=True,
        check_booking=False,
    )
    return await search_doctors_for_booking(db, p)


async def search_doctors_r3_booking(
    db: AsyncSession,
    room_id: UUID,
    date: date_type,
    time: time_type,
    role: str = "doctor",
    location_id: Optional[UUID] = None,
    check_location: bool = False,
    check_timeslot: bool = False,
) -> List[Dict[str, Any]]:
    """R1 (+ optional location) + optional R2 + R3 booking conflict."""
    p = DoctorSearchParams(
        room_id=room_id,
        location_id=location_id,
        role=role,
        date=date,
        time=time,
        check_location=check_location,
        check_timeslot=check_timeslot,
        check_booking=True,
    )
    return await search_doctors_for_booking(db, p)
