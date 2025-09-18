"""Appointment model for medical appointments."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

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
    modality = Column(String(50), nullable=False)  # e.g., "in-person", "virtual", "phone"
    state = Column(String(50), nullable=False)  # e.g., "scheduled", "confirmed", "cancelled", "completed"
    notification_state = Column(String(50), nullable=True)  # e.g., "sent", "pending", "failed"
    appointment_type = Column(String(100), nullable=True)  # e.g., "consultation", "follow-up", "emergency"
    clinic_id = Column(String(100), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Flexible custom fields for tenant-specific data
    custom_fields = Column(JSONB, nullable=False, default=dict)
    
    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, start={self.start_utc}, patient_doc={self.patient_document_number})>"
