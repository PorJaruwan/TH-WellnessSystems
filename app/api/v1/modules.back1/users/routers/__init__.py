from __future__ import annotations

from fastapi import APIRouter

from .user_profiles_search_router import router as user_profiles_search_router
from .user_profiles_read_router import router as user_profiles_read_router
from .user_profiles_router import router as user_profiles_router

from .groups_search_router import router as groups_search_router
from .groups_read_router import router as groups_read_router
from .groups_router import router as groups_router

from .roles_search_router import router as roles_search_router
from .roles_read_router import router as roles_read_router
from .roles_router import router as roles_router

from .permissions_search_router import router as permissions_search_router
from .permissions_read_router import router as permissions_read_router
from .permissions_router import router as permissions_router

from .user_groups_search_router import router as user_groups_search_router
from .user_groups_read_router import router as user_groups_read_router
from .user_groups_router import router as user_groups_router

from .user_roles_search_router import router as user_roles_search_router
from .user_roles_read_router import router as user_roles_read_router
from .user_roles_router import router as user_roles_router

from .role_permissions_search_router import router as role_permissions_search_router
from .role_permissions_read_router import router as role_permissions_read_router
from .role_permissions_router import router as role_permissions_router

from .group_roles_search_router import router as group_roles_search_router
from .group_roles_read_router import router as group_roles_read_router
from .group_roles_router import router as group_roles_router


router = APIRouter(prefix="/users", tags=["User_Settings"])

router.include_router(user_profiles_search_router, prefix="/profiles")
router.include_router(user_profiles_read_router, prefix="/profiles")
router.include_router(user_profiles_router, prefix="/profiles")

router.include_router(groups_search_router, prefix="/groups")
router.include_router(groups_read_router, prefix="/groups")
router.include_router(groups_router, prefix="/groups")

router.include_router(roles_search_router, prefix="/roles")
router.include_router(roles_read_router, prefix="/roles")
router.include_router(roles_router, prefix="/roles")

router.include_router(permissions_search_router, prefix="/permissions")
router.include_router(permissions_read_router, prefix="/permissions")
router.include_router(permissions_router, prefix="/permissions")

router.include_router(user_groups_search_router, prefix="/user_groups")
router.include_router(user_groups_read_router, prefix="/user_groups")
router.include_router(user_groups_router, prefix="/user_groups")

router.include_router(user_roles_search_router, prefix="/user_roles")
router.include_router(user_roles_read_router, prefix="/user_roles")
router.include_router(user_roles_router, prefix="/user_roles")

router.include_router(role_permissions_search_router, prefix="/role_permissions")
router.include_router(role_permissions_read_router, prefix="/role_permissions")
router.include_router(role_permissions_router, prefix="/role_permissions")

router.include_router(group_roles_search_router, prefix="/group_roles")
router.include_router(group_roles_read_router, prefix="/group_roles")
router.include_router(group_roles_router, prefix="/group_roles")

__all__ = ["router"]
