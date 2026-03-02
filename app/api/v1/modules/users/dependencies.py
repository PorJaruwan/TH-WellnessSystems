from __future__ import annotations

from app.api.v1.modules.users.services import (
    UserProfilesSearchService, UserProfilesReadService, UserProfilesService,
    GroupsSearchService, GroupsReadService, GroupsService,
    RolesSearchService, RolesReadService, RolesService,
    PermissionsSearchService, PermissionsReadService, PermissionsService,
    UserGroupsSearchService, UserGroupsReadService, UserGroupsService,
    UserRolesSearchService, UserRolesReadService, UserRolesService,
    RolePermissionsSearchService, RolePermissionsReadService, RolePermissionsService,
    GroupRolesSearchService, GroupRolesReadService, GroupRolesService,
)

# NOTE: Supabase repository is created inside each service by default.
# If later you want to inject DB/session, modify services to accept repo.

def get_user_profiles_search_service() -> UserProfilesSearchService:
    return UserProfilesSearchService()

def get_user_profiles_read_service() -> UserProfilesReadService:
    return UserProfilesReadService()

def get_user_profiles_service() -> UserProfilesService:
    return UserProfilesService()

def get_groups_search_service() -> GroupsSearchService:
    return GroupsSearchService()

def get_groups_read_service() -> GroupsReadService:
    return GroupsReadService()

def get_groups_service() -> GroupsService:
    return GroupsService()

def get_roles_search_service() -> RolesSearchService:
    return RolesSearchService()

def get_roles_read_service() -> RolesReadService:
    return RolesReadService()

def get_roles_service() -> RolesService:
    return RolesService()

def get_permissions_search_service() -> PermissionsSearchService:
    return PermissionsSearchService()

def get_permissions_read_service() -> PermissionsReadService:
    return PermissionsReadService()

def get_permissions_service() -> PermissionsService:
    return PermissionsService()

def get_user_groups_search_service() -> UserGroupsSearchService:
    return UserGroupsSearchService()

def get_user_groups_read_service() -> UserGroupsReadService:
    return UserGroupsReadService()

def get_user_groups_service() -> UserGroupsService:
    return UserGroupsService()

def get_user_roles_search_service() -> UserRolesSearchService:
    return UserRolesSearchService()

def get_user_roles_read_service() -> UserRolesReadService:
    return UserRolesReadService()

def get_user_roles_service() -> UserRolesService:
    return UserRolesService()

def get_role_permissions_search_service() -> RolePermissionsSearchService:
    return RolePermissionsSearchService()

def get_role_permissions_read_service() -> RolePermissionsReadService:
    return RolePermissionsReadService()

def get_role_permissions_service() -> RolePermissionsService:
    return RolePermissionsService()

def get_group_roles_search_service() -> GroupRolesSearchService:
    return GroupRolesSearchService()

def get_group_roles_read_service() -> GroupRolesReadService:
    return GroupRolesReadService()

def get_group_roles_service() -> GroupRolesService:
    return GroupRolesService()
