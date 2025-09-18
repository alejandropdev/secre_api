"""Request ID middleware for tracking requests."""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID and track request timing."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID and track timing."""
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Track start time
        start_time = time.time()
        
        # Add request ID to logger context
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate latency
        latency = time.time() - start_time
        
        # Add timing info to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{latency:.4f}s"
        
        # Log request completion
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency": latency,
            }
        )
        
        return response
