from __future__ import annotations

from typing import TypeAlias

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.users.models.dtos import (
    UserGroupDTO, UserRoleDTO, RolePermissionDTO, GroupRoleDTO
)

UserGroupsSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[UserGroupDTO]]
UserGroupsGetEnvelope: TypeAlias = SuccessEnvelope[dict]
UserGroupsCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
UserGroupsUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
UserGroupsDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

UserRolesSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[UserRoleDTO]]
UserRolesGetEnvelope: TypeAlias = SuccessEnvelope[dict]
UserRolesCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
UserRolesUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
UserRolesDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

RolePermissionsSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[RolePermissionDTO]]
RolePermissionsGetEnvelope: TypeAlias = SuccessEnvelope[dict]
RolePermissionsCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
RolePermissionsUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
RolePermissionsDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

GroupRolesSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[GroupRoleDTO]]
GroupRolesGetEnvelope: TypeAlias = SuccessEnvelope[dict]
GroupRolesCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
GroupRolesUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
GroupRolesDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

__all__ = [
    "UserGroupsSearchEnvelope","UserGroupsGetEnvelope","UserGroupsCreateEnvelope","UserGroupsUpdateEnvelope","UserGroupsDeleteEnvelope",
    "UserRolesSearchEnvelope","UserRolesGetEnvelope","UserRolesCreateEnvelope","UserRolesUpdateEnvelope","UserRolesDeleteEnvelope",
    "RolePermissionsSearchEnvelope","RolePermissionsGetEnvelope","RolePermissionsCreateEnvelope","RolePermissionsUpdateEnvelope","RolePermissionsDeleteEnvelope",
    "GroupRolesSearchEnvelope","GroupRolesGetEnvelope","GroupRolesCreateEnvelope","GroupRolesUpdateEnvelope","GroupRolesDeleteEnvelope",
]
