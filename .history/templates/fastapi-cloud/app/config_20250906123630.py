"""
Application Configuration
=======================

Centralized configuration management using Pydantic Settings.
Supports environment variables, .env files, and multiple environments.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    Automatically loads from .env file and environment variables.
    """
    
    # ===================================================================
    # APPLICATION SETTINGS
    # ===================================================================
    APP_NAME: str = "FastAPI Cloud Template"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Production-ready FastAPI template for cloud-native applications"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # ===================================================================
    # SECURITY SETTINGS
    # ===================================================================
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production",
        env="SECRET_KEY",
        min_length=32
    )
    JWT_SECRET_KEY: str = Field(
        default="jwt-secret-key-change-in-production",
        env="JWT_SECRET_KEY",
        min_length=32
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = Field(default=60 * 24, env="JWT_EXPIRE_MINUTES")  # 24 hours
    JWT_REFRESH_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_EXPIRE_DAYS")
    SESSION_MAX_AGE: int = Field(default=60 * 60 * 24, env="SESSION_MAX_AGE")  # 24 hours
    
    # Password requirements
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    PASSWORD_REQUIRE_DIGITS: bool = Field(default=True, env="PASSWORD_REQUIRE_DIGITS")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")
    
    # ===================================================================
    # DATABASE SETTINGS
    # ===================================================================
    # PostgreSQL
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(default="fastapi", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="password", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="fastapi_db", env="POSTGRES_DB")
    POSTGRES_SSL_MODE: str = Field(default="prefer", env="POSTGRES_SSL_MODE")
    
    # MongoDB
    MONGODB_HOST: str = Field(default="localhost", env="MONGODB_HOST")
    MONGODB_PORT: int = Field(default=27017, env="MONGODB_PORT")
    MONGODB_USER: Optional[str] = Field(default=None, env="MONGODB_USER")
    MONGODB_PASSWORD: Optional[str] = Field(default=None, env="MONGODB_PASSWORD")
    MONGODB_DB: str = Field(default="fastapi_mongo", env="MONGODB_DB")
    
    # Redis
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_SSL: bool = Field(default=False, env="REDIS_SSL")
    
    # ===================================================================
    # CORS AND SECURITY HEADERS
    # ===================================================================
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000,http://localhost:8080",
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: str = Field(
        default="localhost,127.0.0.1,0.0.0.0",
        env="ALLOWED_HOSTS"
    )
    
    # ===================================================================
    # RATE LIMITING
    # ===================================================================
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    RATE_LIMIT_STORAGE: str = Field(default="redis", env="RATE_LIMIT_STORAGE")
    
    # ===================================================================
    # EMAIL SETTINGS
    # ===================================================================
    MAIL_USERNAME: Optional[str] = Field(default=None, env="MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = Field(default=None, env="MAIL_PASSWORD")
    MAIL_FROM: Optional[str] = Field(default=None, env="MAIL_FROM")
    MAIL_SERVER: str = Field(default="smtp.gmail.com", env="MAIL_SERVER")
    MAIL_PORT: int = Field(default=587, env="MAIL_PORT")
    MAIL_STARTTLS: bool = Field(default=True, env="MAIL_STARTTLS")
    MAIL_SSL_TLS: bool = Field(default=False, env="MAIL_SSL_TLS")
    
    # ===================================================================
    # CLOUD SETTINGS
    # ===================================================================
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(default=None, env="GOOGLE_APPLICATION_CREDENTIALS")
    GCP_PROJECT_ID: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")
    GCP_STORAGE_BUCKET: Optional[str] = Field(default=None, env="GCP_STORAGE_BUCKET")
    
    # Azure
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = Field(default=None, env="AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER: Optional[str] = Field(default=None, env="AZURE_STORAGE_CONTAINER")
    
    # ===================================================================
    # MONITORING & OBSERVABILITY
    # ===================================================================
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PATH: str = Field(default="/metrics", env="METRICS_PATH")
    ENABLE_TRACING: bool = Field(default=False, env="ENABLE_TRACING")
    JAEGER_ENDPOINT: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    
    # ===================================================================
    # FEATURE FLAGS
    # ===================================================================
    ENABLE_REGISTRATION: bool = Field(default=True, env="ENABLE_REGISTRATION")
    ENABLE_EMAIL_VERIFICATION: bool = Field(default=False, env="ENABLE_EMAIL_VERIFICATION")
    ENABLE_PASSWORD_RESET: bool = Field(default=True, env="ENABLE_PASSWORD_RESET")
    ENABLE_RATE_LIMITING: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    ENABLE_API_DOCS: bool = Field(default=True, env="ENABLE_API_DOCS")
    
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
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level setting."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    @validator("WORKERS")
    def validate_workers(cls, v, values):
        """Validate number of workers."""
        if v < 1:
            raise ValueError("Workers must be at least 1")
        if values.get("ENVIRONMENT") == "development" and v > 1:
            # Force single worker in development for debugging
            return 1
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


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
        "python_version": os.sys.version,
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
