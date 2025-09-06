"""
User Management Router
=====================

CRUD operations for user management with proper authorization.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
import structlog

from app.models.user_simple import UserResponse, UserCreate
from app.routers.auth import get_current_user
from app.config import get_settings

router = APIRouter()
logger = structlog.get_logger(__name__)
settings = get_settings()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user)
):
    """Get list of users (admin only)."""
    # In real implementation, check admin permissions
    
    # Simulate user data
    users = [
        UserResponse(
            id=1,
            username="demo",
            email="demo@example.com",
            is_active=True,
            created_at="2024-01-01T00:00:00Z"
        ),
        UserResponse(
            id=2,
            username="admin",
            email="admin@example.com",
            is_active=True,
            created_at="2024-01-01T00:00:00Z"
        )
    ]
    
    return users[skip:skip + limit]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get user by ID."""
    # In real implementation, fetch from database
    if user_id == current_user["user_id"] or user_id == 1:
        return UserResponse(
            id=user_id,
            username="demo",
            email="demo@example.com",
            is_active=True,
            created_at="2024-01-01T00:00:00Z"
        )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update user information."""
    # Check if user can update (self or admin)
    if user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # In real implementation, update in database
    logger.info("User updated", user_id=user_id, username=current_user["username"])
    
    return UserResponse(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        is_active=user_data.is_active,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        created_at="2024-01-01T00:00:00Z"
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete user account (admin only)."""
    # In real implementation, check admin permissions
    # and soft delete user
    
    logger.info("User deleted", user_id=user_id, admin=current_user["username"])
    
    return {"message": "User deleted successfully"}


@router.get("/{user_id}/profile", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed user profile."""
    if user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only access your own profile"
        )
    
    return UserResponse(
        id=user_id,
        username=current_user["username"],
        email=f"{current_user['username']}@example.com",
        is_active=True,
        created_at="2024-01-01T00:00:00Z"
    )
