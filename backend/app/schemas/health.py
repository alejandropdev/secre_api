"""Health check Pydantic schemas."""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class HealthCheckSchema(BaseSchema):
    """Schema for health check responses."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    database: Optional[str] = Field(None, description="Database status")
    dependencies: Optional[Dict[str, str]] = Field(None, description="External dependencies status")


class ServiceInfoSchema(BaseSchema):
    """Schema for service information."""
    
    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    description: str = Field(..., description="Service description")
    docs_url: str = Field(..., description="API documentation URL")
    health_url: str = Field(..., description="Health check URL")
