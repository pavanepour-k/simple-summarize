USER_ROLES = {"admin_api_key": "admin", "pro_api_key": "pro", "user_api_key": "user"}


def get_user_role(api_key: str) -> str:
    # Get user role based on the provided API key
    return USER_ROLES.get(api_key, "user")
