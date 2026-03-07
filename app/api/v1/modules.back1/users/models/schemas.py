from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

# =========================================================
# Schemas (request models): Create / Update
# =========================================================

class UserProfileCreate(BaseModel):
    id: UUID
    user_id: UUID
    company_code: str
    location_id: UUID
    department_id: UUID
    preferred_language: str
    preferred_currency: str
    full_name: str
    avatar_url: str | None = None
    email: str | None = None
    password_hash: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class UserProfileUpdate(BaseModel):
    location_id: UUID | None = None
    department_id: UUID | None = None
    preferred_language: str | None = None
    preferred_currency: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None
    email: str | None = None
    password_hash: str | None = None
    is_active: bool | None = None
    updated_at: datetime | None = None

class GroupCreate(BaseModel):
    id: UUID
    group_name: str
    description: str | None = None
    company_code: str

class GroupUpdate(BaseModel):
    group_name: str | None = None
    description: str | None = None
    company_code: str | None = None

class RoleCreate(BaseModel):
    id: UUID
    role_name: str
    description: str | None = None
    company_code: str

class RoleUpdate(BaseModel):
    role_name: str | None = None
    description: str | None = None
    company_code: str | None = None

class PermissionCreate(BaseModel):
    id: UUID
    permission_code: str
    description: str | None = None
    company_code: str

class PermissionUpdate(BaseModel):
    permission_code: str | None = None
    description: str | None = None
    company_code: str | None = None

class UserGroupCreate(BaseModel):
    id: UUID
    profile_id: UUID
    group_id: UUID

class UserGroupUpdate(BaseModel):
    profile_id: UUID | None = None
    group_id: UUID | None = None

class UserRoleCreate(BaseModel):
    id: UUID
    profile_id: UUID
    role_id: UUID

class UserRoleUpdate(BaseModel):
    profile_id: UUID | None = None
    role_id: UUID | None = None

class RolePermissionCreate(BaseModel):
    id: UUID
    role_id: UUID
    permission_id: UUID

class RolePermissionUpdate(BaseModel):
    role_id: UUID | None = None
    permission_id: UUID | None = None

class GroupRoleCreate(BaseModel):
    id: UUID
    group_id: UUID
    role_id: UUID

class GroupRoleUpdate(BaseModel):
    group_id: UUID | None = None
    role_id: UUID | None = None
