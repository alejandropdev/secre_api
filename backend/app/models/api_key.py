"""API Key model for authentication."""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class ApiKey(Base, TimestampMixin):
    """API Key model for tenant authentication."""
    
    __tablename__ = "api_key"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    key_hash = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def is_revoked(self) -> bool:
        """Check if the API key is revoked."""
        return self.revoked_at is not None
