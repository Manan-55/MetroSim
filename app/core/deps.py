from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Generator, Optional
from app.database import get_db
from app.core.auth import security, get_current_user_from_token, AuthenticationError
from app.models.user import User
import redis
from app.config import settings

# Redis connection
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

def get_redis() -> redis.Redis:
    """Get Redis client"""
    return redis_client

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        return get_current_user_from_token(credentials.credentials, db)
    except AuthenticationError as e:
        raise e

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if credentials is None:
        return None
    
    try:
        return get_current_user_from_token(credentials.credentials, db)
    except AuthenticationError:
        return None

class DatabaseDependency:
    """Database dependency with automatic rollback on error"""
    
    def __init__(self):
        self.db: Optional[Session] = None
    
    def __enter__(self) -> Session:
        self.db = next(get_db())
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        self.db.close()
