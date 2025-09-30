"""Tenant-specific lookup models for appointment types and clinics."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base, TenantMixin, TimestampMixin


class TenantAppointmentType(Base, TenantMixin, TimestampMixin):
    """Tenant-specific appointment type lookup table."""
    
    __tablename__ = "tenant_appointment_type"
    
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(String(10), nullable=False, default="true")  # "true" or "false"
    
    def __repr__(self) -> str:
        return f"<TenantAppointmentType(id={self.id}, code={self.code}, name={self.name}, tenant_id={self.tenant_id})>"


class TenantClinic(Base, TenantMixin, TimestampMixin):
    """Tenant-specific clinic lookup table."""
    
    __tablename__ = "tenant_clinic"
    
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(String(10), nullable=False, default="true")  # "true" or "false"
    
    def __repr__(self) -> str:
        return f"<TenantClinic(id={self.id}, code={self.code}, name={self.name}, tenant_id={self.tenant_id})>"
