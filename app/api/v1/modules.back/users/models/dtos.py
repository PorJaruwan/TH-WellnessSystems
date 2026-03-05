from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# DTOs (response models)
# =========================================================

class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserProfileDTO(ORMBaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: UUID
    user_id: Optional[UUID] = None
    full_name: Optional[str] = None
    company_code: str
    location_id: UUID | None = None
    department_id: UUID | None = None
    preferred_language: str | None = None
    preferred_currency: str | None = None
    avatar_url: str | None = None
    email: str | None = None
    is_active: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class GroupDTO(ORMBaseModel):
    id: UUID
    group_name: str
    description: str | None = None
    company_code: str | None = None

class RoleDTO(ORMBaseModel):
    id: UUID
    role_name: str
    description: str | None = None
    company_code: str | None = None

class PermissionDTO(ORMBaseModel):
    id: UUID
    permission_code: str
    description: str | None = None
    company_code: str | None = None

class UserGroupDTO(ORMBaseModel):
    id: UUID
    profile_id: UUID
    group_id: UUID

class UserRoleDTO(ORMBaseModel):
    id: UUID
    profile_id: UUID
    role_id: UUID

class RolePermissionDTO(ORMBaseModel):
    id: UUID
    role_id: UUID
    permission_id: UUID

class GroupRoleDTO(ORMBaseModel):
    id: UUID
    group_id: UUID
    role_id: UUID
