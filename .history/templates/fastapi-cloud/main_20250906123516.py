"""
FastAPI Cloud-Native Template
==========================

Production-ready FastAPI application with security, scalability, and cloud-native features.
Perfect for hackathons, prototypes, and production deployments.

Features:
- JWT Authentication & Authorization
- Rate Limiting & Security Middleware  
- Multi-database Support (PostgreSQL, MongoDB, Redis)
- Async Request Handling
- API Documentation (OpenAPI/Swagger)
- Health Checks & Monitoring
- Docker & Kubernetes Ready
- Multi-cloud Deployment Support

Author: AI Assistant
Created: 2025
License: MIT
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.middleware.security import SecurityMiddleware
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.routers import auth, users, health, api
from app.database import init_databases, close_databases
from app.utils.metrics import setup_metrics

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Initialize settings
settings = get_settings()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour", "100/minute"],
    storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    strategy="fixed-window"
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler for startup and shutdown events.
    Manages database connections and other resources.
    """
    # Startup
    logger.info("🚀 Starting FastAPI Cloud Template")
    
    try:
        # Initialize databases
        await init_databases()
        logger.info("✅ Database connections established")
        
        # Setup metrics
        setup_metrics()
        logger.info("✅ Metrics collection initialized")
        
        # Application ready
        logger.info("🎯 Application ready to serve requests")
        
        yield
        
    except Exception as e:
        logger.error("❌ Failed to start application", error=str(e))
        sys.exit(1)
    
    finally:
        # Shutdown
        logger.info("🛑 Shutting down application")
        await close_databases()
        logger.info("✅ Database connections closed")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application with all middleware and routes.
    
    Returns:
        FastAPI: Configured application instance
    """
    # Create FastAPI app with lifespan management
    app = FastAPI(
        title="FastAPI Cloud Template",
        description="Production-ready FastAPI template for cloud-native applications",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan
    )
    
    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Security middleware (first for early protection)
    app.add_middleware(SecurityMiddleware)
    
    # Trusted host middleware
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS.split(",")
        )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"]
    )
    
    # Session middleware for authentication
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        max_age=settings.SESSION_MAX_AGE,
        same_site="lax",
        https_only=settings.ENVIRONMENT == "production"
    )
    
    # Custom middleware
    app.add_middleware(AuthMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(api.router, prefix="/api/v1", tags=["API"])
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with application information."""
        return {
            "message": "FastAPI Cloud Template",
            "version": "1.0.0",
            "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
            "health": "/health",
            "status": "operational"
        }
    
    # Metrics endpoint for Prometheus
    @app.get("/metrics", tags=["Monitoring"])
    async def metrics():
        """Prometheus metrics endpoint."""
        return JSONResponse(
            content=generate_latest().decode("utf-8"),
            media_type=CONTENT_TYPE_LATEST
        )
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler for unhandled errors."""
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True
        )
        
        if settings.ENVIRONMENT == "production":
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(exc),
                    "type": exc.__class__.__name__,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    """
    Development server entry point.
    Use this for local development only.
    """
    if settings.ENVIRONMENT == "development":
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            use_colors=True
        )
    else:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=settings.PORT,
            workers=settings.WORKERS,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=False,  # We handle logging in middleware
            server_header=False,
            date_header=False
        )
