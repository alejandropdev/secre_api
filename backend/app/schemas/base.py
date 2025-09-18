"""Base Pydantic schemas and common types."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class EventType(str):
    """Event type enumeration."""
    PATIENT = "PATIENT"
    APPOINTMENT = "APPOINTMENT"


class ActionType(str):
    """Action type enumeration."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"


class CustomFieldsSchema(BaseModel):
    """Schema for custom fields (flexible JSONB data)."""
    
    def __init__(self, **data: Any):
        super().__init__(**data)
    
    class Config:
        extra = "allow"  # Allow additional fields


class TimestampSchema(BaseModel):
    """Schema with timestamp fields."""
    
    created_at: datetime
    updated_at: datetime


class TenantContextSchema(BaseModel):
    """Schema for tenant context information."""
    
    tenant_id: UUID
    tenant_name: str
    api_key_id: UUID


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""
    
    error: str
    detail: Optional[str] = None
    trace_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
