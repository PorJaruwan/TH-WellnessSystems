# app/api/v1/models/patient_masterdata_model.py

from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class AlertDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    alert_name: Optional[str] = None
    alert_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AllergyDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    allergy_name: Optional[str] = None
    description: Optional[str] = None
    allergy_type: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SourceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_name: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PatientTypeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SaleStaffDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sale_person_name: Optional[str] = None
    department_name: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MarketingStaffDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    marketing_name: Optional[str] = None
    campaign: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
