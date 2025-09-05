"""
Database configuration and session management.

Provides async SQLAlchemy engine, session factory, and dependency injection helpers.
"""

from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Async engine for production use
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=30,
)

# Sync engine for migrations and testing
sync_engine = create_engine(
    settings.database_url.replace("postgresql+asyncpg://", "postgresql://"),
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=30,
)

# Session factories
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=True,
    autocommit=False,
)


# Event listeners for connection management
@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database-specific connection parameters."""
    if "postgresql" in settings.database_url:
        # Enable PostGIS and other extensions
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET timezone = 'Asia/Kolkata'")
            cursor.execute("SET search_path = public")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.
    
    Yields:
        AsyncSession: Database session for async operations
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> Generator[Session, None, None]:
    """
    Dependency to get sync database session.
    
    Yields:
        Session: Database session for sync operations
    """
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_db() -> None:
    """Initialize database connection and verify connectivity."""
    try:
        async with async_engine.begin() as conn:
            # Test connection
            await conn.execute("SELECT 1")
        print("✅ Database connection established successfully")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise


async def close_db() -> None:
    """Close database connections."""
    await async_engine.dispose()
    sync_engine.dispose()
    print("✅ Database connections closed")


# Health check functions
async def check_db_health() -> bool:
    """
    Check database health.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False


def check_sync_db_health() -> bool:
    """
    Check sync database health.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        with SessionLocal() as session:
            session.execute("SELECT 1")
            return True
    except Exception:
        return False