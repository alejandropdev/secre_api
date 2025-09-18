"""Audit log Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class AuditLogResponseSchema(BaseSchema):
    """Schema for audit log responses."""
    
    id: UUID
    tenant_id: UUID
    resource_type: str
    resource_id: UUID
    action: str
    api_key_id: Optional[UUID] = None
    before_snapshot: Optional[Dict[str, Any]] = None
    after_snapshot: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class AuditLogListResponseSchema(BaseSchema):
    """Schema for audit log list responses."""
    
    audit_logs: List[AuditLogResponseSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class AuditLogSearchSchema(BaseSchema):
    """Schema for audit log search filters."""
    
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Page size")
