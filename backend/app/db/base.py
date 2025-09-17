"""Database base classes and utilities."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Base class for all database models."""
    
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimestampMixin:
    """Mixin for timestamp fields."""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantMixin:
    """Mixin for tenant isolation."""
    
    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())
