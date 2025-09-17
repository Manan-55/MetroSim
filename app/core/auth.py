from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.security import verify_token
from app.models.user import User
from sqlalchemy.orm import Session

security = HTTPBearer()

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class AuthorizationError(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

def get_current_user_from_token(token: str, db: Session) -> User:
    """Get current user from JWT token"""
    payload = verify_token(token)
    if payload is None:
        raise AuthenticationError()
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise AuthenticationError()
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    return user

def require_roles(*required_roles: str):
    """Decorator to require specific roles"""
    def decorator(func):
        def wrapper(current_user: User, *args, **kwargs):
            if not any(role in current_user.roles for role in required_roles):
                raise AuthorizationError(f"Required roles: {', '.join(required_roles)}")
            return func(current_user, *args, **kwargs)
        return wrapper
    return decorator

def require_permissions(*required_permissions: str):
    """Decorator to require specific permissions"""
    def decorator(func):
        def wrapper(current_user: User, *args, **kwargs):
            user_permissions = set()
            for role in current_user.roles:
                user_permissions.update(role.permissions)
            
            if not all(perm in user_permissions for perm in required_permissions):
                raise AuthorizationError(f"Required permissions: {', '.join(required_permissions)}")
            return func(current_user, *args, **kwargs)
        return wrapper
    return decorator
