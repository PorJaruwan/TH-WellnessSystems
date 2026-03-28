from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import ConfigDict, Field

from app.api.v1.models._envelopes.base_envelopes import ORMBaseModel


class DoctorLocationResponse(ORMBaseModel):
    location_id: UUID
    location_name: str


class DoctorByServiceItemResponse(ORMBaseModel):
    doctor_id: UUID
    staff_name: str
    role: str
    license_number: Optional[str] = None
    specialty: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    main_location_id: Optional[UUID] = None

    service_id: UUID
    service_code: Optional[str] = None
    service_name: str
    service_name_th: Optional[str] = None
    service_name_en: Optional[str] = None
    duration_minutes: int

    locations: List[DoctorLocationResponse] = Field(default_factory=list)


class DoctorByServiceListResponse(ORMBaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[DoctorByServiceItemResponse] = Field(default_factory=list)
    total: int = 0