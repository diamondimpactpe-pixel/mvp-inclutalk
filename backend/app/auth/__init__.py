"""
Authentication module
"""
from app.auth.security import verify_password, get_password_hash, validate_password_strength
from app.auth.jwt import create_access_token, create_refresh_token, decode_token, verify_token_type
from app.auth.middleware import (
    get_current_user,
    get_current_active_user,
    require_role,
    require_admin,
    require_superadmin,
    verify_institution_access
)

__all__ = [
    "verify_password",
    "get_password_hash",
    "validate_password_strength",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token_type",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_admin",
    "require_superadmin",
    "verify_institution_access",
]
