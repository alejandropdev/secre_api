"""Base Pydantic schemas and common types."""

from datetime import datetime
from enum import Enum
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


class EventType(str, Enum):
    """Event type enumeration."""
    PATIENT = "PATIENT"
    APPOINTMENT = "APPOINTMENT"


class ActionType(str, Enum):
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
    
    error: str = Field(..., description="Mensaje de error principal", example="Validation error")
    detail: Optional[str] = Field(None, description="Detalles adicionales del error", example="Patient with document 12345678 already exists")
    trace_id: Optional[str] = Field(None, description="ID de trazabilidad para debugging", example="550e8400-e29b-41d4-a716-446655440000")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp del error en formato ISO 8601 UTC", example="2024-01-15T10:30:00Z")
    field: Optional[str] = Field(None, description="Campo específico que causó el error de validación", example="document_number")
    
    class Config:
        schema_extra = {
            "examples": {
                "validation_error": {
                    "error": "Validation error",
                    "detail": "Patient with document 12345678 already exists",
                    "trace_id": "550e8400-e29b-41d4-a716-446655440001",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "field": "document_number"
                },
                "not_found_error": {
                    "error": "Patient 550e8400-e29b-41d4-a716-446655440000 not found",
                    "trace_id": "550e8400-e29b-41d4-a716-446655440002",
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "unauthorized_error": {
                    "error": "API key required. Provide X-Api-Key header.",
                    "trace_id": "550e8400-e29b-41d4-a716-446655440003",
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "internal_error": {
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred",
                    "trace_id": "550e8400-e29b-41d4-a716-446655440004",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            }
        }
