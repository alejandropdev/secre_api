"""Patient model for medical data."""

import uuid
from datetime import date
from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base, TenantMixin, TimestampMixin


class Patient(Base, TenantMixin, TimestampMixin):
    """Patient model with canonical fields and flexible custom_fields."""
    
    __tablename__ = "patient"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    
    # Canonical fields
    first_name = Column(String(255), nullable=False)
    second_name = Column(String(255), nullable=True)
    first_last_name = Column(String(255), nullable=False)
    second_last_name = Column(String(255), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender_id = Column(Integer, nullable=True)
    document_type_id = Column(Integer, nullable=False)
    document_number = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    eps_id = Column(String(100), nullable=True)  # Health insurance provider
    habeas_data = Column(Boolean, default=False, nullable=False)
    
    # Flexible custom fields for tenant-specific data
    custom_fields = Column(JSONB, nullable=False, default=dict)
    
    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, name={self.first_name} {self.first_last_name})>"
