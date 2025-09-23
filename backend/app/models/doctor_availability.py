"""Doctor availability model for calendar management."""

import uuid
from datetime import datetime, time
from sqlalchemy import Boolean, Column, Integer, String, Time, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base, TimestampMixin


class DoctorAvailability(Base, TimestampMixin):
    """Doctor availability model for managing work hours and blocked times."""
    
    __tablename__ = "doctor_availability"
    
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
    doctor_document_type_id = Column(Integer, nullable=False)
    doctor_document_number = Column(String(50), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    appointment_duration_minutes = Column(Integer, default=30, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    custom_fields = Column(JSONB, default=dict)


class DoctorBlockedTime(Base, TimestampMixin):
    """Doctor blocked time model for managing unavailable periods."""
    
    __tablename__ = "doctor_blocked_time"
    
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
    doctor_document_type_id = Column(Integer, nullable=False)
    doctor_document_number = Column(String(50), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    custom_fields = Column(JSONB, default=dict)
