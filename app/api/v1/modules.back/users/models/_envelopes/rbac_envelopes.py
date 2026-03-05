from __future__ import annotations

from typing import TypeAlias

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.users.models.dtos import GroupDTO, RoleDTO, PermissionDTO

GroupsSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[GroupDTO]]
GroupsGetEnvelope: TypeAlias = SuccessEnvelope[dict]
GroupsCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
GroupsUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
GroupsDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

RolesSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[RoleDTO]]
RolesGetEnvelope: TypeAlias = SuccessEnvelope[dict]
RolesCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
RolesUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
RolesDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

PermissionsSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[PermissionDTO]]
PermissionsGetEnvelope: TypeAlias = SuccessEnvelope[dict]
PermissionsCreateEnvelope: TypeAlias = SuccessEnvelope[dict]
PermissionsUpdateEnvelope: TypeAlias = SuccessEnvelope[dict]
PermissionsDeleteEnvelope: TypeAlias = SuccessEnvelope[dict]

__all__ = [
    "GroupsSearchEnvelope","GroupsGetEnvelope","GroupsCreateEnvelope","GroupsUpdateEnvelope","GroupsDeleteEnvelope",
    "RolesSearchEnvelope","RolesGetEnvelope","RolesCreateEnvelope","RolesUpdateEnvelope","RolesDeleteEnvelope",
    "PermissionsSearchEnvelope","PermissionsGetEnvelope","PermissionsCreateEnvelope","PermissionsUpdateEnvelope","PermissionsDeleteEnvelope",
]
