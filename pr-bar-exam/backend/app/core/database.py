"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()


def get_async_database_url() -> str:
    """
    Convert DATABASE_URL to async format for SQLAlchemy.
    Vercel Postgres URLs use 'postgres://' but SQLAlchemy async needs 'postgresql+asyncpg://'.
    
    Returns:
        Properly formatted async database URL
    """
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    url = settings.DATABASE_URL
    
    # Convert postgres:// to postgresql+asyncpg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Handle Vercel's specific URL format with query parameters
    # Vercel URLs often have ?sslmode=require at the end
    if "sslmode" not in url and "?" not in url:
        url += "?sslmode=require"
    
    return url


# Create async engine
try:
    database_url = get_async_database_url()
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    # Create a dummy engine for startup - will fail on actual use
    engine = None


# Create async session factory
if engine:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
else:
    AsyncSessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    Yields:
        AsyncSession instance
    """
    if not AsyncSessionLocal:
        raise RuntimeError("Database not configured. Please set DATABASE_URL environment variable.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Supabase admin client (optional)
supabase_admin: Optional[object] = None

try:
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
        from supabase import create_client, Client
        supabase_admin: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        logger.info("Supabase admin client created successfully")
    else:
        logger.info("Supabase not configured - realtime features will be unavailable")
except ImportError:
    logger.warning("Supabase package not installed - realtime features will be unavailable")
except Exception as e:
    logger.error(f"Failed to create Supabase client: {e}")


async def init_db():
    """
    Initialize database tables.
    Call this on startup to create all tables.
    """
    if not engine:
        logger.error("Cannot initialize database - engine not created")
        return
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


async def close_db():
    """
    Close database connections.
    Call this on shutdown.
    """
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")