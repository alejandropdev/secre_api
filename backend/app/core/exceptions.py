"""Custom exceptions and error handling."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BaseAPIException(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.trace_id = trace_id or str(uuid.uuid4())
        super().__init__(message)


class ValidationAPIException(BaseAPIException):
    """Exception for validation errors (4xx)."""
    
    def __init__(
        self,
        message: str,
        detail: Optional[str] = None,
        field: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            trace_id=trace_id,
        )
        self.field = field


class NotFoundAPIException(BaseAPIException):
    """Exception for not found errors (404)."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        detail: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            trace_id=trace_id,
        )


class UnauthorizedAPIException(BaseAPIException):
    """Exception for unauthorized errors (401)."""
    
    def __init__(
        self,
        message: str = "Unauthorized",
        detail: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            trace_id=trace_id,
        )


class ForbiddenAPIException(BaseAPIException):
    """Exception for forbidden errors (403)."""
    
    def __init__(
        self,
        message: str = "Forbidden",
        detail: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            trace_id=trace_id,
        )


class InternalServerAPIException(BaseAPIException):
    """Exception for internal server errors (5xx)."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        detail: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            trace_id=trace_id,
        )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str
    detail: Optional[str] = None
    trace_id: str
    timestamp: str
    field: Optional[str] = None


async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions."""
    
    # Get request context
    request_id = getattr(request.state, "request_id", None)
    tenant_id = getattr(request.state, "tenant_context", None).tenant_id if getattr(request.state, "tenant_context", None) else None
    
    # Log the error
    logger.error(
        f"API Exception: {exc.message}",
        extra={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "trace_id": exc.trace_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "detail": exc.detail,
        }
    )
    
    # Create error response
    error_response = ErrorResponse(
        error=exc.message,
        detail=exc.detail,
        trace_id=exc.trace_id,
        timestamp=exc.timestamp if hasattr(exc, 'timestamp') and exc.timestamp else datetime.utcnow().isoformat(),
        field=getattr(exc, 'field', None),
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(exclude_none=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    
    # Get request context
    request_id = getattr(request.state, "request_id", None)
    tenant_id = getattr(request.state, "tenant_context", None).tenant_id if getattr(request.state, "tenant_context", None) else None
    trace_id = str(uuid.uuid4())
    
    # Log the error
    logger.error(
        f"HTTP Exception: {exc.detail}",
        extra={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "trace_id": trace_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    # Create error response
    error_response = ErrorResponse(
        error=exc.detail,
        trace_id=trace_id,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(exclude_none=True),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    
    # Get request context
    request_id = getattr(request.state, "request_id", None)
    tenant_id = getattr(request.state, "tenant_context", None).tenant_id if getattr(request.state, "tenant_context", None) else None
    trace_id = str(uuid.uuid4())
    
    # Log the error
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "trace_id": trace_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
        exc_info=True,
    )
    
    # Create error response
    error_response = ErrorResponse(
        error="Internal server error",
        detail="An unexpected error occurred",
        trace_id=trace_id,
        timestamp=datetime.utcnow().isoformat(),
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict(exclude_none=True),
    )
