"""
Health Check Router
==================

Comprehensive health checks for the FastAPI application including
database connections, external services, and system metrics.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import time
import psutil
import structlog

from app.database import get_database_status
from app.config import get_settings, get_environment_info

router = APIRouter()
logger = structlog.get_logger(__name__)
settings = get_settings()


@router.get("/", response_model=Dict[str, Any])
async def basic_health():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": settings.APP_NAME,
        "version": settings.VERSION
    }


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health():
    """Detailed health check with database and system status."""
    try:
        # Get database status
        db_status = await get_database_status()
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine overall health
        all_dbs_healthy = all(db_status.values())
        cpu_healthy = cpu_percent < 90
        memory_healthy = memory.percent < 90
        disk_healthy = disk.percent < 90
        
        overall_status = "healthy" if all([
            all_dbs_healthy,
            cpu_healthy,
            memory_healthy,
            disk_healthy
        ]) else "unhealthy"
        
        response_data = {
            "status": overall_status,
            "timestamp": time.time(),
            "service": settings.APP_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "databases": db_status,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "checks": {
                "databases": "healthy" if all_dbs_healthy else "unhealthy",
                "cpu": "healthy" if cpu_healthy else "unhealthy", 
                "memory": "healthy" if memory_healthy else "unhealthy",
                "disk": "healthy" if disk_healthy else "unhealthy"
            }
        }
        
        status_code = 200 if overall_status == "healthy" else 503
        return JSONResponse(content=response_data, status_code=status_code)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            },
            status_code=503
        )


@router.get("/ready")
async def readiness_probe():
    """Kubernetes readiness probe - checks if app can serve requests."""
    try:
        db_status = await get_database_status()
        
        # App is ready if at least one database is available
        ready = any(db_status.values())
        
        if ready:
            return {"status": "ready"}
        else:
            raise HTTPException(
                status_code=503,
                detail="Application not ready - no databases available"
            )
            
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Application not ready: {str(e)}"
        )


@router.get("/live")
async def liveness_probe():
    """Kubernetes liveness probe - checks if app is alive."""
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime": time.time()  # In a real app, track actual uptime
    }


@router.get("/info")
async def application_info():
    """Get detailed application information."""
    return get_environment_info()
