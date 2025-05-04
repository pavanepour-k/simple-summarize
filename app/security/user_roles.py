USER_ROLES = {
    "admin_api_key": "admin",
    "pro_api_key": "pro",
    "user_api_key": "user"
}

def get_user_role(api_key: str) -> str:
    return USER_ROLES.get(api_key, "user")