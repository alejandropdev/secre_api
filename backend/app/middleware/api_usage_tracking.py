"""API Usage Tracking Middleware for monitoring API key usage metrics."""

import logging
import time
from typing import Optional
from uuid import UUID

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.api_key_usage_service import ApiKeyUsageService
from app.db.session import get_db

logger = logging.getLogger(__name__)


class ApiUsageTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track API usage metrics for each request."""
    
    async def dispatch(self, request: Request, call_next):
        """Track API usage for each request."""
        
        start_time = time.time()
        
        # Skip tracking for certain paths
        if self._should_skip_tracking(request):
            return await call_next(request)
        
        # Get tenant context from request state (set by auth middleware)
        tenant_context = getattr(request.state, 'tenant_context', None)
        
        if not tenant_context or tenant_context.api_key_id == "master":
            # Skip tracking for master API key or requests without tenant context
            return await call_next(request)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Track the usage
            await self._track_usage(
                request=request,
                response=response,
                tenant_context=tenant_context,
                response_time_ms=response_time_ms,
            )
            
            return response
            
        except Exception as e:
            # Track error responses too
            response_time_ms = int((time.time() - start_time) * 1000)
            
            try:
                await self._track_usage(
                    request=request,
                    response=None,
                    tenant_context=tenant_context,
                    response_time_ms=response_time_ms,
                    status_code=500,  # Internal server error
                )
            except Exception as track_error:
                logger.error(f"Failed to track usage for error response: {track_error}")
            
            raise e
    
    def _should_skip_tracking(self, request: Request) -> bool:
        """Determine if we should skip tracking for this request."""
        
        skip_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        }
        
        # Skip if path is in skip list
        if request.url.path in skip_paths:
            return True
        
        # Skip if it's a static file or documentation
        if request.url.path.startswith(("/static/", "/docs", "/redoc")):
            return True
        
        return False
    
    async def _track_usage(
        self,
        request: Request,
        response: Optional[Response],
        tenant_context,
        response_time_ms: int,
        status_code: Optional[int] = None,
    ) -> None:
        """Track usage metrics for the request."""
        
        try:
            # Get database session
            async for db in get_db():
                usage_service = ApiKeyUsageService(db)
                
                # Determine status code
                if status_code is None and response:
                    status_code = response.status_code
                elif status_code is None:
                    status_code = 200  # Default to 200 if no response
                
                # Extract endpoint path (remove query parameters)
                endpoint = request.url.path
                
                # Get client IP
                ip_address = self._get_client_ip(request)
                
                # Get user agent
                user_agent = request.headers.get("user-agent", "")
                
                # Track the usage
                await usage_service.track_request(
                    api_key_id=UUID(tenant_context.api_key_id),
                    tenant_id=UUID(tenant_context.tenant_id),
                    endpoint=endpoint,
                    method=request.method,
                    status_code=status_code,
                    response_time_ms=response_time_ms,
                    ip_address=ip_address,
                    user_agent=user_agent[:500],  # Truncate to fit database field
                )
                
                break  # Exit the async generator
                
        except Exception as e:
            logger.error(f"Failed to track API usage: {e}")
            # Don't raise the exception to avoid breaking the request
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP address from request headers."""
        
        # Check for forwarded headers first (for reverse proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None
