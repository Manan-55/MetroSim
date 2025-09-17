"""
Core functionality for the Train Management System.
"""

from app.core.auth import (
    get_current_user,
    get_current_active_user,
    authenticate_user,
    create_access_token,
    verify_token
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_jwt_token,
    verify_jwt_token
)
from app.core.deps import (
    get_db,
    get_redis,
    get_current_user_dependency,
    require_role
)

__all__ = [
    # Authentication
    "get_current_user",
    "get_current_active_user", 
    "authenticate_user",
    "create_access_token",
    "verify_token",
    
    # Security
    "verify_password",
    "get_password_hash",
    "create_jwt_token",
    "verify_jwt_token",
    
    # Dependencies
    "get_db",
    "get_redis",
    "get_current_user_dependency",
    "require_role"
]
