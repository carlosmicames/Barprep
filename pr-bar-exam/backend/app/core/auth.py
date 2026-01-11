"""
Authentication and authorization utilities - SIMPLIFIED FOR TESTING.
This version allows all requests without authentication.
Replace with full auth.py for production.
"""
from fastapi import Depends, HTTPException, status
from typing import Optional
from pydantic import BaseModel


class UserContext(BaseModel):
    """User context model for authenticated requests."""
    user_id: int = 1
    email: str = "test@example.com"
    username: str = "testuser"
    is_admin: bool = True  # Everyone is admin for testing
    
    class Config:
        from_attributes = True


async def get_current_user() -> UserContext:
    """
    Returns a test user - NO AUTHENTICATION FOR TESTING.
    
    Returns:
        UserContext with test user information
    """
    return UserContext(
        user_id=1,
        email="test@example.com",
        username="testuser",
        is_admin=True
    )


async def verify_admin(
    current_user: UserContext = Depends(get_current_user)
) -> UserContext:
    """
    Always returns user as admin - FOR TESTING ONLY.
    
    Args:
        current_user: Current user (always admin in test mode)
        
    Returns:
        UserContext
    """
    return current_user


async def get_optional_user() -> Optional[UserContext]:
    """
    Returns test user for optional auth endpoints.
    
    Returns:
        UserContext with test user
    """
    return UserContext(
        user_id=1,
        email="test@example.com",
        username="testuser",
        is_admin=True
    )