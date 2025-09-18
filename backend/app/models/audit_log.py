"""Audit log model for tracking changes."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    """Audit log for tracking all write operations."""
    
    __tablename__ = "audit_log"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    
    # Actor information
    api_key_id = Column(UUID(as_uuid=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Resource information
    resource_type = Column(String(100), nullable=False)  # e.g., "patient", "appointment"
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., "create", "update", "delete"
    
    # Change details
    before_snapshot = Column(JSONB, nullable=True)
    after_snapshot = Column(JSONB, nullable=True)
    
    # Request context
    request_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, resource={self.resource_type}:{self.resource_id}, action={self.action})>"
