"""Appointment model for medical appointments."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TenantMixin, TimestampMixin


class Appointment(Base, TenantMixin, TimestampMixin):
    """Appointment model with canonical fields and flexible custom_fields."""
    
    __tablename__ = "appointment"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    
    # Canonical fields
    start_utc = Column(DateTime(timezone=True), nullable=False)
    end_utc = Column(DateTime(timezone=True), nullable=False)
    
    # Patient identification
    patient_document_type_id = Column(Integer, nullable=False)
    patient_document_number = Column(String(50), nullable=False)
    
    # Doctor identification
    doctor_document_type_id = Column(Integer, nullable=False)
    doctor_document_number = Column(String(50), nullable=False)
    
    # Appointment details
    modality_id = Column(Integer, ForeignKey("appointment_modality.id"), nullable=False)
    state_id = Column(Integer, ForeignKey("appointment_state.id"), nullable=False)
    notification_state = Column(String(50), nullable=True)  # e.g., "sent", "pending", "failed"
    appointment_type_id = Column(Integer, ForeignKey("tenant_appointment_type.id"), nullable=True)
    clinic_id = Column(Integer, ForeignKey("tenant_clinic.id"), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Flexible custom fields for tenant-specific data
    custom_fields = Column(JSONB, nullable=False, default=dict)
    
    # Relationships
    modality = relationship("AppointmentModality", foreign_keys=[modality_id])
    state = relationship("AppointmentState", foreign_keys=[state_id])
    appointment_type = relationship("TenantAppointmentType", foreign_keys=[appointment_type_id])
    clinic = relationship("TenantClinic", foreign_keys=[clinic_id])
    
    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, start={self.start_utc}, patient_doc={self.patient_document_number})>"
