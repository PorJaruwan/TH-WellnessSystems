# app/api/v1/users/user_model.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# ==============================
# user_profiles
# ==============================
class UserProfilesCreateModel(BaseModel):
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
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserProfilesUpdateModel(BaseModel):
    location_id: UUID
    department_id: UUID
    preferred_language: str
    preferred_currency: str
    full_name: str
    avatar_url: str | None = None
    email: str | None = None
    password_hash: str | None = None
    is_active: bool
    updated_at: datetime

class UserProfilesResponseModel(BaseModel):
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
    is_active: bool
    created_at: datetime
    updated_at: datetime

### json test create request
# {
#   "id": "193ec369-ce5a-4a88-a73e-907feabc3d8c",
#   "user_id": "414ed6ae-a2aa-4548-b73a-66ce240c0089",
#   "company_code": "LNV",
#   "location_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
#   "department_id": "24dbbb8a-2afb-4bf6-a9f9-a24fc3285994",
#   "preferred_language": "TH",
#   "preferred_currency": "THB",
#   "full_name": "kanchit k.",
#   "avatar_url": "url",
#   "email": "string@gmail.com",
#   "password_hash": "string",
#   "is_active": true,
#   "created_at": "2025-07-24T06:03:33.050Z",
#   "updated_at": "2025-07-24T06:03:33.050Z"
# }
### json test update request
# {
#   "location_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
#   "department_id": "24dbbb8a-2afb-4bf6-a9f9-a24fc3285994",
#   "preferred_language": "TH",
#   "preferred_currency": "THB",
#   "full_name": "kanchit k.",
#   "avatar_url": "url",
#   "email": "string@gmail.com",
#   "password_hash": "string",
#   "is_active": true,
#   "updated_at": "2025-07-24T06:03:33.050Z"
# }

# ==============================
# groups
# ==============================
class GroupsCreateModel(BaseModel):
    id: UUID
    group_name: str
    description: str
    company_code: str

class GroupsUpdateModel(BaseModel):
    group_name: str
    description: str
    company_code: str

# ==============================
# roles
# ==============================
class RolesCreateModel(BaseModel):
    id: UUID
    role_name: str
    description: str
    company_code: str

class RolesUpdateModel(BaseModel):
    role_name: str
    description: str
    company_code: str

# ==============================
# permissions
# ==============================
class PermissionsCreateModel(BaseModel):
    id: UUID
    permission_code: str
    description: str
    company_code: str

class PermissionsUpdateModel(BaseModel):
    permission_code: str
    description: str
    company_code: str

# ==============================
# user_groups
# ==============================
class UserGroupsCreateModel(BaseModel):
    id: UUID
    profile_id: UUID
    group_id: UUID

class UserGroupsUpdateModel(BaseModel):
    profile_id: UUID
    group_id: UUID

# ==============================
# user_roles
# ==============================
class UserRolesCreateModel(BaseModel):
    id: UUID
    profile_id: UUID
    role_id: UUID

class UserRolesUpdateModel(BaseModel):
    profile_id: UUID
    role_id: UUID

# ==============================
# role_permissions
# ==============================
class RolePermissionsCreateModel(BaseModel):
    id: UUID
    role_id: UUID
    permission_id: UUID

class RolePermissionsUpdateModel(BaseModel):
    role_id: UUID
    permission_id: UUID

# ==============================
# group_roles
# ==============================
class GroupRolesCreateModel(BaseModel):
    id: UUID
    group_id: UUID
    role_id: UUID

class GroupRolesUpdateModel(BaseModel):
    group_id: UUID
    role_id: UUID

# ==============================
# protected_routes
# ==============================
class ProtectedRoutesCreateModel(BaseModel):
    id: UUID
    route_path: str
    http_method: str
    permission_id: UUID
    module_name: str
    description: str | None = None
    is_active: bool

class ProtectedRoutesUpdateModel(BaseModel):
    route_path: str
    http_method: str
    permission_id: UUID
    module_name: str
    description: str | None = None
    is_active: bool    