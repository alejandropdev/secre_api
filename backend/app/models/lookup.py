"""Lookup tables for common enums and reference data."""

import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class DocumentType(Base, TimestampMixin):
    """Document type lookup table."""
    
    __tablename__ = "document_type"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<DocumentType(id={self.id}, code={self.code}, name={self.name})>"


class Gender(Base, TimestampMixin):
    """Gender lookup table."""
    
    __tablename__ = "gender"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Gender(id={self.id}, code={self.code}, name={self.name})>"


class AppointmentModality(Base, TimestampMixin):
    """Appointment modality lookup table."""
    
    __tablename__ = "appointment_modality"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AppointmentModality(id={self.id}, code={self.code}, name={self.name})>"


class AppointmentState(Base, TimestampMixin):
    """Appointment state lookup table."""
    
    __tablename__ = "appointment_state"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AppointmentState(id={self.id}, code={self.code}, name={self.name})>"
