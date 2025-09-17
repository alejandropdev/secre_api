"""Tenant model for multi-tenancy."""

import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    """Tenant model for multi-tenant isolation."""
    
    __tablename__ = "tenant"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
