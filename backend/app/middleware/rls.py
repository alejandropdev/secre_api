"""Row-Level Security (RLS) middleware."""

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RLSMiddleware(BaseHTTPMiddleware):
    """Middleware to set tenant context for RLS."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Set tenant context in database session."""
        
        # Skip RLS setup for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get tenant context from request state (set by auth middleware)
        tenant_context = getattr(request.state, "tenant_context", None)
        
        if tenant_context:
            # Set tenant context in database session
            # This will be handled by the database session hook
            logger.debug(f"Setting tenant context: {tenant_context.tenant_id}")
        else:
            logger.warning("No tenant context found for request")
        
        response = await call_next(request)
        return response
