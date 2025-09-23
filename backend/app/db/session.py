"""Database session management."""

import logging
from contextvars import ContextVar
from typing import Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Context variable for tenant ID
tenant_context: ContextVar[Optional[str]] = ContextVar("tenant_context", default=None)

# Create sync engine for migrations
sync_engine = create_engine(
    settings.effective_database_url,
    pool_pre_ping=True,
    echo=settings.debug,
)

# Create async engine for application
async_engine = create_async_engine(
    settings.effective_database_url.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    echo=settings.debug,
)

# Create session factories
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Add RLS setup to async engine
@event.listens_for(async_engine.sync_engine, "connect")
def set_rls_context(dbapi_connection, connection_record):
    """Set up RLS context for each database connection."""
    cursor = dbapi_connection.cursor()
    try:
        # Enable RLS and set up the app schema
        cursor.execute("SET search_path TO public, app;")
        cursor.execute("SET row_security = on;")
    finally:
        cursor.close()


async def get_db() -> AsyncSession:
    """Get database session with RLS context."""
    async with AsyncSessionLocal() as session:
        # Set tenant context for RLS
        current_tenant = tenant_context.get()
        if current_tenant:
            await session.execute(text("SET LOCAL app.tenant_id = :tenant_id"), {"tenant_id": current_tenant})
            logger.debug(f"Set tenant context in DB session: {current_tenant}")
        
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Get synchronous database session for migrations."""
    with sessionmaker(bind=sync_engine)() as session:
        yield session


def set_tenant_context(tenant_id: str) -> None:
    """Set tenant context for the current request."""
    tenant_context.set(tenant_id)
