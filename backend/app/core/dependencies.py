"""Core dependencies for the application."""

import logging
from typing import Optional

from fastapi import Depends, Request

from app.core.logging import ContextualLoggerAdapter
from app.middleware.auth import TenantContext, get_current_tenant


def get_logger(request: Request) -> logging.Logger:
    """Get a logger with request context."""
    
    # Get base logger
    logger = logging.getLogger(__name__)
    
    # Get request context
    request_id = getattr(request.state, "request_id", None)
    tenant_context = getattr(request.state, "tenant_context", None)
    
    # Build context
    context = {}
    if request_id:
        context["request_id"] = request_id
    if tenant_context:
        context["tenant_id"] = tenant_context.tenant_id
        context["api_key_id"] = tenant_context.api_key_id
    
    # Return contextual logger
    return ContextualLoggerAdapter(logger, context)


def get_request_context(
    request: Request,
    tenant_context: Optional[TenantContext] = Depends(get_current_tenant),
) -> dict:
    """Get request context for audit logging."""
    
    return {
        "request_id": getattr(request.state, "request_id", None),
        "tenant_id": tenant_context.tenant_id if tenant_context else None,
        "api_key_id": tenant_context.api_key_id if tenant_context else None,
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
