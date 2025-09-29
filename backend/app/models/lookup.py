"""Lookup tables for common enums and reference data."""

from sqlalchemy import Column, Integer, String, Text

from app.db.base import Base, TimestampMixin


class DocumentType(Base, TimestampMixin):
    """Document type lookup table."""
    
    __tablename__ = "document_type"
    
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<DocumentType(id={self.id}, code={self.code}, name={self.name})>"


class Gender(Base, TimestampMixin):
    """Gender lookup table."""
    
    __tablename__ = "gender"
    
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Gender(id={self.id}, code={self.code}, name={self.name})>"


class AppointmentModality(Base, TimestampMixin):
    """Appointment modality lookup table."""
    
    __tablename__ = "appointment_modality"
    
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AppointmentModality(id={self.id}, code={self.code}, name={self.name})>"


class AppointmentState(Base, TimestampMixin):
    """Appointment state lookup table."""
    
    __tablename__ = "appointment_state"
    
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AppointmentState(id={self.id}, code={self.code}, name={self.name})>"
