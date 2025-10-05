"""API Key Usage Metrics model for tracking API usage."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Date, Index
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class ApiKeyUsage(Base, TimestampMixin):
    """API Key usage metrics for tracking requests and usage patterns."""
    
    __tablename__ = "api_key_usage"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    api_key_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    
    # Request details
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PATCH, DELETE
    status_code = Column(Integer, nullable=False)
    
    # Usage metrics
    request_count = Column(Integer, default=1, nullable=False)
    response_time_ms = Column(Integer, nullable=True)  # Response time in milliseconds
    
    # Time tracking
    usage_date = Column(Date, nullable=False, index=True)  # Date of usage for daily aggregation
    usage_hour = Column(Integer, nullable=True)  # Hour of day (0-23) for hourly analysis
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_api_key_usage_date', 'api_key_id', 'usage_date'),
        Index('idx_api_key_usage_endpoint', 'api_key_id', 'endpoint'),
        Index('idx_tenant_usage_date', 'tenant_id', 'usage_date'),
        Index('idx_usage_date_hour', 'usage_date', 'usage_hour'),
    )
    
    def __repr__(self) -> str:
        return f"<ApiKeyUsage(api_key_id={self.api_key_id}, endpoint={self.endpoint}, count={self.request_count})>"
