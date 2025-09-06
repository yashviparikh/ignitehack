"""
Database Configuration and Connection Management
==============================================

Handles multiple database connections (PostgreSQL, MongoDB, Redis)
with connection pooling, health checks, and async support.
"""

import asyncio
from typing import Optional
import asyncpg
import motor.motor_asyncio
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import structlog

from app.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# ===================================================================
# DATABASE ENGINES AND CONNECTIONS
# ===================================================================

# PostgreSQL (SQLAlchemy + asyncpg)
postgres_engine = None
async_session_maker = None

# MongoDB (Motor)
mongodb_client = None
mongodb_database = None

# Redis (aioredis)
redis_client = None


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


# ===================================================================
# POSTGRESQL CONNECTION
# ===================================================================

async def init_postgres():
    """Initialize PostgreSQL connection with SQLAlchemy."""
    global postgres_engine, async_session_maker
    
    try:
        postgres_engine = create_async_engine(
            settings.postgres_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20,
            future=True
        )
        
        async_session_maker = async_sessionmaker(
            postgres_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test connection
        async with postgres_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ PostgreSQL connected successfully")
        
    except Exception as e:
        logger.error("❌ Failed to connect to PostgreSQL", error=str(e))
        raise


async def close_postgres():
    """Close PostgreSQL connection."""
    global postgres_engine
    if postgres_engine:
        await postgres_engine.dispose()
        logger.info("✅ PostgreSQL connection closed")


async def get_postgres_session() -> AsyncSession:
    """Get PostgreSQL session for dependency injection."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ===================================================================
# MONGODB CONNECTION
# ===================================================================

async def init_mongodb():
    """Initialize MongoDB connection with Motor."""
    global mongodb_client, mongodb_database
    
    try:
        mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
        )
        
        mongodb_database = mongodb_client[settings.MONGODB_DB]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        
        logger.info("✅ MongoDB connected successfully")
        
    except Exception as e:
        logger.error("❌ Failed to connect to MongoDB", error=str(e))
        raise


async def close_mongodb():
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("✅ MongoDB connection closed")


def get_mongodb() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Get MongoDB database for dependency injection."""
    return mongodb_database


# ===================================================================
# REDIS CONNECTION
# ===================================================================

async def init_redis():
    """Initialize Redis connection with aioredis."""
    global redis_client
    
    try:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        await redis_client.ping()
        
        logger.info("✅ Redis connected successfully")
        
    except Exception as e:
        logger.error("❌ Failed to connect to Redis", error=str(e))
        raise


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("✅ Redis connection closed")


def get_redis() -> aioredis.Redis:
    """Get Redis client for dependency injection."""
    return redis_client


# ===================================================================
# DATABASE HEALTH CHECKS
# ===================================================================

async def check_postgres_health() -> bool:
    """Check PostgreSQL connection health."""
    try:
        async with postgres_engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error("PostgreSQL health check failed", error=str(e))
        return False


async def check_mongodb_health() -> bool:
    """Check MongoDB connection health."""
    try:
        await mongodb_client.admin.command('ping')
        return True
    except Exception as e:
        logger.error("MongoDB health check failed", error=str(e))
        return False


async def check_redis_health() -> bool:
    """Check Redis connection health."""
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return False


async def get_database_status() -> dict:
    """Get comprehensive database status."""
    return {
        "postgres": await check_postgres_health(),
        "mongodb": await check_mongodb_health(),
        "redis": await check_redis_health()
    }


# ===================================================================
# INITIALIZATION AND CLEANUP
# ===================================================================

async def init_databases():
    """Initialize all database connections."""
    logger.info("🔌 Initializing database connections...")
    
    # Initialize connections concurrently
    await asyncio.gather(
        init_postgres(),
        init_mongodb(),
        init_redis(),
        return_exceptions=True
    )
    
    logger.info("✅ All database connections initialized")


async def close_databases():
    """Close all database connections."""
    logger.info("🔌 Closing database connections...")
    
    # Close connections concurrently
    await asyncio.gather(
        close_postgres(),
        close_mongodb(),
        close_redis(),
        return_exceptions=True
    )
    
    logger.info("✅ All database connections closed")


# ===================================================================
# DEPENDENCY INJECTION HELPERS
# ===================================================================

class DatabaseDependencies:
    """Database dependency injection helper."""
    
    @staticmethod
    async def get_postgres() -> AsyncSession:
        """Get PostgreSQL session."""
        async for session in get_postgres_session():
            yield session
    
    @staticmethod
    def get_mongodb() -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Get MongoDB database."""
        return get_mongodb()
    
    @staticmethod
    def get_redis() -> aioredis.Redis:
        """Get Redis client."""
        return get_redis()


# Create dependency instances
db = DatabaseDependencies()
