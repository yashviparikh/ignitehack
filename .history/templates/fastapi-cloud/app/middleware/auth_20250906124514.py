"""
Authentication Middleware
========================

JWT token validation and user context middleware.
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for processing JWT tokens."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process authentication for requests."""
        # Skip auth for public endpoints
        public_paths = ["/", "/docs", "/redoc", "/openapi.json", "/health", "/metrics"]
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Process request normally (auth handled by dependencies)
        response = await call_next(request)
        return response
