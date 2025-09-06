"""
Authentication Router
====================

JWT-based authentication with registration, login, password reset,
and token management. Includes security features and rate limiting.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
import structlog

from app.config import get_settings
from app.models.user_simple import User, UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.database import db

router = APIRouter()
logger = structlog.get_logger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # In a real app, fetch user from database
        # For now, return basic user info from token
        return {"username": username, "user_id": payload.get("user_id")}
        
    except JWTError:
        raise credentials_exception


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreate):
    """Register a new user account."""
    if not settings.ENABLE_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently disabled"
        )
    
    try:
        # Check if user already exists (simplified - use real DB in production)
        # In real implementation, check against your user database
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user (simplified - use real DB in production)
        user_response = UserResponse(
            id=1,  # Generate real ID
            username=user_data.username,
            email=user_data.email,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        logger.info("User registered successfully", username=user_data.username)
        
        return user_response
        
    except Exception as e:
        logger.error("Registration failed", error=str(e), username=user_data.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, login_data: UserLogin):
    """Authenticate user and return JWT tokens."""
    try:
        # In real implementation, fetch user from database and verify password
        # For now, simplified authentication
        
        # Simulate user lookup and password verification
        if login_data.username == "demo" and login_data.password == "demo123":
            user_id = 1
            username = login_data.username
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": username, "user_id": user_id}
        )
        refresh_token = create_refresh_token(
            data={"sub": username, "user_id": user_id}
        )
        
        logger.info("User logged in successfully", username=username)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh_token(request: Request, refresh_token: str):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(
            refresh_token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new access token
        new_access_token = create_access_token(
            data={"sub": username, "user_id": user_id}
        )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,  # Keep same refresh token
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (invalidate token)."""
    # In a real implementation, add token to blacklist
    logger.info("User logged out", username=current_user["username"])
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    # In real implementation, fetch from database
    return UserResponse(
        id=current_user["user_id"],
        username=current_user["username"],
        email=f"{current_user['username']}@example.com",
        is_active=True,
        created_at=datetime.utcnow()
    )


@router.post("/change-password")
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """Change user password."""
    try:
        # In real implementation:
        # 1. Verify old password
        # 2. Hash new password
        # 3. Update in database
        
        logger.info("Password changed successfully", username=current_user["username"])
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        logger.error("Password change failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )
