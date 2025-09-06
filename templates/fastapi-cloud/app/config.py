"""
Application Configuration
=======================

Centralized configuration management using Pydantic Settings.
Supports environment variables, .env files, and multiple environments.
"""

import os
import sys
from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    Automatically loads from .env file and environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # ===================================================================
    # APPLICATION SETTINGS
    # ===================================================================
    APP_NAME: str = "FastAPI Cloud Template"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Production-ready FastAPI template for cloud-native applications"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8000
    WORKERS: int = 1
    LOG_LEVEL: str = "INFO"
    
    # ===================================================================
    # SECURITY SETTINGS
    # ===================================================================
    SECRET_KEY: str = "your-super-secret-key-change-in-production-make-it-32-chars-long"
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production-make-it-32-chars-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    SESSION_MAX_AGE: int = 60 * 60 * 24  # 24 hours
    
    # Password requirements
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # ===================================================================
    # DATABASE SETTINGS
    # ===================================================================
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "fastapi"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "fastapi_db"
    POSTGRES_SSL_MODE: str = "prefer"
    
    # MongoDB
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    MONGODB_DB: str = "fastapi_mongo"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_SSL: bool = False
    
    # ===================================================================
    # CORS AND SECURITY HEADERS
    # ===================================================================
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://localhost:8080"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,0.0.0.0"
    
    # ===================================================================
    # RATE LIMITING
    # ===================================================================
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_STORAGE: str = "redis"
    
    # ===================================================================
    # EMAIL SETTINGS
    # ===================================================================
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    # ===================================================================
    # CLOUD SETTINGS
    # ===================================================================
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCP_PROJECT_ID: Optional[str] = None
    GCP_STORAGE_BUCKET: Optional[str] = None
    
    # Azure
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: Optional[str] = None
    
    # ===================================================================
    # MONITORING & OBSERVABILITY
    # ===================================================================
    ENABLE_METRICS: bool = True
    METRICS_PATH: str = "/metrics"
    ENABLE_TRACING: bool = False
    JAEGER_ENDPOINT: Optional[str] = None
    
    # ===================================================================
    # FEATURE FLAGS
    # ===================================================================
    ENABLE_REGISTRATION: bool = True
    ENABLE_EMAIL_VERIFICATION: bool = False
    ENABLE_PASSWORD_RESET: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_API_DOCS: bool = True
    
    # ===================================================================
    # COMPUTED PROPERTIES
    # ===================================================================
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            f"?sslmode={self.POSTGRES_SSL_MODE}"
        )
    
    @property
    def postgres_sync_url(self) -> str:
        """Get synchronous PostgreSQL connection URL."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            f"?sslmode={self.POSTGRES_SSL_MODE}"
        )
    
    @property
    def mongodb_url(self) -> str:
        """Get MongoDB connection URL."""
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            return (
                f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}"
                f"@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
            )
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        protocol = "rediss" if self.REDIS_SSL else "redis"
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"{protocol}://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ===================================================================
    # VALIDATORS
    # ===================================================================
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level setting."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    @field_validator("WORKERS")
    @classmethod
    def validate_workers(cls, v):
        """Validate number of workers."""
        if v < 1:
            raise ValueError("Workers must be at least 1")
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    Uses LRU cache to avoid re-reading environment on every call.
    
    Returns:
        Settings: Application configuration
    """
    return Settings()


# Create settings instance for immediate use
settings = get_settings()


def get_environment_info() -> dict:
    """
    Get environment information for debugging and monitoring.
    
    Returns:
        dict: Environment information
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "python_version": sys.version,
        "workers": settings.WORKERS,
        "log_level": settings.LOG_LEVEL,
        "features": {
            "registration": settings.ENABLE_REGISTRATION,
            "email_verification": settings.ENABLE_EMAIL_VERIFICATION,
            "password_reset": settings.ENABLE_PASSWORD_RESET,
            "rate_limiting": settings.ENABLE_RATE_LIMITING,
            "api_docs": settings.ENABLE_API_DOCS,
            "metrics": settings.ENABLE_METRICS,
            "tracing": settings.ENABLE_TRACING,
        }
    }
