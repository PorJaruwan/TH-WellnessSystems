from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class DoctorByServiceQueryParams(BaseModel):
    service_id: Optional[UUID] = Field(default=None)
    service_code: Optional[str] = Field(default=None, max_length=100)
    location_id: Optional[UUID] = Field(default=None)
    primary_only: bool = Field(default=False)
    company_code: Optional[str] = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_input(self) -> "DoctorByServiceQueryParams":
        if not self.service_id and not self.service_code:
            raise ValueError("service_id or service_code is required")

        # multi-tenant safe:
        # services unique = (company_code, service_code)
        if self.service_code and not self.company_code:
            raise ValueError("company_code is required when searching by service_code")

        return self