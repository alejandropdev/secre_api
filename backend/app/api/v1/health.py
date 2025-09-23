"""Health check endpoints."""

import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthCheckSchema, ServiceInfoSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/health", tags=["Health"])

# Store startup time for uptime calculation
startup_time = time.time()


@router.get("/", response_model=HealthCheckSchema)
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
):
    """Detailed health check with database connectivity."""
    
    uptime = time.time() - startup_time
    database_status = "unknown"
    
    try:
        # Test database connectivity
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        database_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = "unhealthy"
    
    return HealthCheckSchema(
        status="healthy" if database_status == "healthy" else "degraded",
        version=settings.version,
        timestamp=datetime.utcnow(),
        uptime=uptime,
        database=database_status,
    )


