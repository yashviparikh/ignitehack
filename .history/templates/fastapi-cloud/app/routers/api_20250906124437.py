"""
API Router
==========

Main API routes for application functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import structlog

from app.routers.auth import get_current_user
from app.config import get_settings

router = APIRouter()
logger = structlog.get_logger(__name__)
settings = get_settings()


@router.get("/status")
async def api_status():
    """Get API status information."""
    return {
        "status": "operational",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "features": {
            "authentication": True,
            "rate_limiting": settings.ENABLE_RATE_LIMITING,
            "api_docs": settings.ENABLE_API_DOCS
        }
    }


@router.get("/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    """Example protected endpoint requiring authentication."""
    return {
        "message": "This is a protected endpoint",
        "user": current_user["username"],
        "timestamp": "2024-01-01T00:00:00Z"
    }


@router.get("/public")
async def public_endpoint():
    """Example public endpoint accessible without authentication."""
    return {
        "message": "This is a public endpoint",
        "timestamp": "2024-01-01T00:00:00Z",
        "info": "No authentication required"
    }
