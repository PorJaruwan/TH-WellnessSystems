# app/api/v1/users/user_service.py
from uuid import UUID
from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

# ==============================
# UserProfiles Services
# ==============================
def post_user_profiles(data: dict):
    return supabase.table("user_profiles").insert(data).execute()

def get_all_user_profiles():
    return supabase.table("user_profiles").select("*").order("full_name", desc=False).execute()

def get_user_profiles_by_id(user_profile_id: str):
    return supabase.table("user_profiles").select("*").eq("id", user_profile_id).execute()

# def get_user_profiles_by_name(full_name: str):
#     return supabase.table("user_profiles").select("*").eq("full_name", full_name).execute()

def put_user_profiles_by_id(user_profile_id: str, updated: dict):
    return supabase.table("user_profiles").update(updated).eq("id", user_profile_id).execute()

def delete_user_profiles_by_id(user_profile_id: str):
    return supabase.table("user_profiles").delete().eq("id", user_profile_id).execute()

# ✅ Search by name with partial match
def search_user_profiles_by_name(full_name: str = ""):
    query = supabase.table("user_profiles").select("id, full_name, email, user_id, company_code, location_id, department_id")
    if full_name:
        query = query.ilike("full_name", f"%{full_name}%")
    return query.execute()

# ✅ Format result to match schema (no first_name/last_name, use full_name directly)
def transform_user_profiles_with_fullname(data: list[dict]) -> list[dict]:
    result = []
    for profile in data:
        result.append({
            "id": profile.get("id"),
            "full_name": profile.get("full_name"),
            "email": profile.get("email"),
            "user_id": profile.get("user_id"),
            "company_code": profile.get("company_code"),
            "location_id": profile.get("location_id"),            
            "department_id": profile.get("department_id"),
        })
    return result


# ==============================
# groups
# ==============================
def post_groups(data: dict):
    return supabase.table("groups").insert(data).execute()

def get_all_groups():
    return supabase.table("groups").select("*").order("group_name", desc=False).execute()

def get_groups_by_id(groups_id: str):
    return supabase.table("groups").select("*").eq("id", groups_id).execute()

def put_groups_by_id(groups_id: str, updated: dict):
    return supabase.table("groups").update(updated).eq("id", groups_id).execute()

def delete_groups_by_id(groups_id: str):
    return supabase.table("groups").delete().eq("id", groups_id).execute()

# ==============================
# roles
# ==============================
def post_roles(data: dict):
    return supabase.table("roles").insert(data).execute()

def get_all_roles():
    return supabase.table("roles").select("*").order("role_name", desc=False).execute()

def get_roles_by_id(roles_id: str):
    return supabase.table("roles").select("*").eq("id", roles_id).execute()

def put_roles_by_id(roles_id: str, updated: dict):
    return supabase.table("roles").update(updated).eq("id", roles_id).execute()

def delete_roles_by_id(roles_id: str):
    return supabase.table("roles").delete().eq("id", roles_id).execute()

# ==============================
# permissions
# ==============================
def post_permissions(data: dict):
    return supabase.table("permissions").insert(data).execute()

def get_all_permissions():
    return supabase.table("permissions").select("*").order("permission_code", desc=False).execute()

def get_permissions_by_id(permissions_id: str):
    return supabase.table("permissions").select("*").eq("id", permissions_id).execute()

def put_permissions_by_id(permissions_id: str, updated: dict):
    return supabase.table("permissions").update(updated).eq("id", permissions_id).execute()

def delete_permissions_by_id(permissions_id: str):
    return supabase.table("permissions").delete().eq("id", permissions_id).execute()

# ==============================
# user_groups
# ==============================
def post_user_groups(data: dict):
    return supabase.table("user_groups").insert(data).execute()

def get_all_user_groups():
    return supabase.table("user_groups").select("*").order("group_id", desc=False).execute()

def get_user_groups_by_id(user_groups_id: str):
    return supabase.table("user_groups").select("*").eq("id", user_groups_id).execute()

def put_user_groups_by_id(user_groups_id: str, updated: dict):
    return supabase.table("user_groups").update(updated).eq("id", user_groups_id).execute()

def delete_user_groups_by_id(user_groups_id: str):
    return supabase.table("user_groups").delete().eq("id", user_groups_id).execute()

# ==============================
# user_roles
# ==============================
def post_user_roles(data: dict):
    return supabase.table("user_roles").insert(data).execute()

def get_all_user_roles():
    return supabase.table("user_roles").select("*").order("role_id", desc=False).execute()

def get_user_roles_by_id(user_roles_id: str):
    return supabase.table("user_roles").select("*").eq("id", user_roles_id).execute()

def put_user_roles_by_id(user_roles_id: str, updated: dict):
    return supabase.table("user_roles").update(updated).eq("id", user_roles_id).execute()

def delete_user_roles_by_id(user_roles_id: str):
    return supabase.table("user_roles").delete().eq("id", user_roles_id).execute()

# ==============================
# role_permissions
# ==============================
def post_role_permissions(data: dict):
    return supabase.table("role_permissions").insert(data).execute()

def get_all_role_permissions():
    return supabase.table("role_permissions").select("*").order("role_id", desc=False).execute()

def get_role_permissions_by_id(role_permissions_id: str):
    return supabase.table("role_permissions").select("*").eq("id", role_permissions_id).execute()

def put_role_permissions_by_id(role_permissions_id: str, updated: dict):
    return supabase.table("role_permissions").update(updated).eq("id", role_permissions_id).execute()

def delete_role_permissions_by_id(role_permissions_id: str):
    return supabase.table("role_permissions").delete().eq("id", role_permissions_id).execute()

# ==============================
# group_roles
# ==============================
def post_group_roles(data: dict):
    return supabase.table("group_roles").insert(data).execute()

def get_all_group_roles():
    return supabase.table("group_roles").select("*").order("group_id", desc=False).execute()

def get_group_roles_by_id(group_roles_id: str):
    return supabase.table("group_roles").select("*").eq("id", group_roles_id).execute()

def put_group_roles_by_id(group_roles_id: str, updated: dict):
    return supabase.table("group_roles").update(updated).eq("id", group_roles_id).execute()

def delete_group_roles_by_id(group_roles_id: str):
    return supabase.table("group_roles").delete().eq("id", group_roles_id).execute()


# ==============================
# protected_routes
# ==============================
def post_protected_routes(data: dict):
    return supabase.table("protected_routes").insert(data).execute()

def get_all_protected_routes():
    return supabase.table("protected_routes").select("*").order("route_path", desc=False).execute()

def get_protected_routes_by_id(protected_routes_id: str):
    return supabase.table("protected_routes").select("*").eq("id", protected_routes_id).execute()

def put_protected_routes_by_id(protected_routes_id: str, updated: dict):
    return supabase.table("protected_routes").update(updated).eq("id", protected_routes_id).execute()

def delete_protected_routes_by_id(protected_routes_id: str):
    return supabase.table("protected_routes").delete().eq("id", protected_routes_id).execute()