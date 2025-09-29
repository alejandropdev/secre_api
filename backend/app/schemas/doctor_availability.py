"""Doctor availability Pydantic schemas."""

from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class DoctorAvailabilityCreateSchema(BaseSchema):
    """Schema for creating doctor availability."""
    
    doctor_document_type_id: int = Field(..., description="Doctor document type ID")
    doctor_document_number: str = Field(..., description="Doctor document number")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    appointment_duration_minutes: int = Field(default=30, ge=15, le=480, description="Appointment duration in minutes")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DoctorAvailabilityResponseSchema(BaseSchema):
    """Schema for doctor availability responses."""
    
    id: UUID
    tenant_id: UUID
    doctor_document_type_id: int
    doctor_document_number: str
    day_of_week: int
    start_time: str
    end_time: str
    appointment_duration_minutes: int
    is_active: bool
    custom_fields: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class DoctorBlockedTimeCreateSchema(BaseSchema):
    """Schema for creating blocked time."""
    
    doctor_document_type_id: int = Field(..., description="Doctor document type ID")
    doctor_document_number: str = Field(..., description="Doctor document number")
    start_datetime: str = Field(..., description="Start datetime in ISO format")
    end_datetime: str = Field(..., description="End datetime in ISO format")
    reason: Optional[str] = Field(None, description="Reason for blocking")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DoctorBlockedTimeResponseSchema(BaseSchema):
    """Schema for blocked time responses."""
    
    id: UUID
    tenant_id: UUID
    doctor_document_type_id: int
    doctor_document_number: str
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str]
    is_active: bool
    custom_fields: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TimeSlotSchema(BaseSchema):
    """Schema for time slots."""
    
    start_datetime: datetime
    end_datetime: datetime
    available: bool


class AvailableTimeSlotsResponseSchema(BaseSchema):
    """Schema for available time slots response."""
    
    doctor_document_type_id: int
    doctor_document_number: str
    date: str
    time_slots: List[TimeSlotSchema]
    total_slots: int
    available_slots: int
