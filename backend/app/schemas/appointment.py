"""Appointment Pydantic schemas matching client payloads."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import ActionType, BaseSchema, EventType


class AppointmentBaseSchema(BaseSchema):
    """Base appointment schema with common fields."""
    
    start_utc: datetime = Field(..., description="Appointment start time in UTC")
    end_utc: datetime = Field(..., description="Appointment end time in UTC")
    patient_document_type_id: int = Field(..., description="Patient document type ID")
    patient_document_number: str = Field(..., min_length=1, max_length=50, description="Patient document number")
    doctor_document_type_id: int = Field(..., description="Doctor document type ID")
    doctor_document_number: str = Field(..., min_length=1, max_length=50, description="Doctor document number")
    modality: str = Field(..., min_length=1, max_length=50, description="Appointment modality")
    state: str = Field(..., min_length=1, max_length=50, description="Appointment state")
    notification_state: Optional[str] = Field(None, max_length=50, description="Notification state")
    appointment_type: Optional[str] = Field(None, max_length=100, description="Appointment type")
    clinic_id: Optional[str] = Field(None, max_length=100, description="Clinic ID")
    comment: Optional[str] = Field(None, description="Appointment comment")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom tenant-specific fields")


class AppointmentCreateSchema(AppointmentBaseSchema):
    """Schema for creating an appointment (matches client payload)."""
    
    event_type: EventType = Field(EventType.APPOINTMENT, description="Event type")
    action_type: ActionType = Field(ActionType.CREATE, description="Action type")
    
    # RFC3339 format fields for client compatibility
    start_appointment: str = Field(..., description="Start appointment in RFC3339 format")
    end_appointment: str = Field(..., description="End appointment in RFC3339 format")
    
    @validator('start_appointment', 'end_appointment')
    def validate_rfc3339_datetime(cls, v):
        """Validate RFC3339 datetime format."""
        try:
            # Parse RFC3339 format (supports both Z and offset)
            if v.endswith('Z'):
                return datetime.fromisoformat(v[:-1] + '+00:00')
            else:
                return datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid RFC3339 datetime format')
    
    @validator('end_utc')
    def validate_end_after_start(cls, v, values):
        """Validate that end time is after start time."""
        if 'start_utc' in values and v <= values['start_utc']:
            raise ValueError('End time must be after start time')
        return v


class AppointmentUpdateSchema(BaseSchema):
    """Schema for updating an appointment."""
    
    event_type: EventType = Field(EventType.APPOINTMENT, description="Event type")
    action_type: ActionType = Field(ActionType.UPDATE, description="Action type")
    
    start_utc: Optional[datetime] = None
    end_utc: Optional[datetime] = None
    patient_document_type_id: Optional[int] = None
    patient_document_number: Optional[str] = Field(None, min_length=1, max_length=50)
    doctor_document_type_id: Optional[int] = None
    doctor_document_number: Optional[str] = Field(None, min_length=1, max_length=50)
    modality: Optional[str] = Field(None, min_length=1, max_length=50)
    state: Optional[str] = Field(None, min_length=1, max_length=50)
    notification_state: Optional[str] = Field(None, max_length=50)
    appointment_type: Optional[str] = Field(None, max_length=100)
    clinic_id: Optional[str] = Field(None, max_length=100)
    comment: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    # RFC3339 format fields for client compatibility
    start_appointment: Optional[str] = Field(None, description="Start appointment in RFC3339 format")
    end_appointment: Optional[str] = Field(None, description="End appointment in RFC3339 format")
    
    @validator('start_appointment', 'end_appointment')
    def validate_rfc3339_datetime(cls, v):
        """Validate RFC3339 datetime format."""
        if v is None:
            return v
        try:
            if v.endswith('Z'):
                return datetime.fromisoformat(v[:-1] + '+00:00')
            else:
                return datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid RFC3339 datetime format')
    
    @validator('end_utc')
    def validate_end_after_start(cls, v, values):
        """Validate that end time is after start time."""
        if v and 'start_utc' in values and values['start_utc'] and v <= values['start_utc']:
            raise ValueError('End time must be after start time')
        return v


class AppointmentResponseSchema(AppointmentBaseSchema):
    """Schema for appointment responses."""
    
    id: UUID
    tenant_id: UUID
    created_at: str
    updated_at: str


class AppointmentListResponseSchema(BaseSchema):
    """Schema for appointment list responses."""
    
    appointments: List[AppointmentResponseSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class AppointmentSearchSchema(BaseSchema):
    """Schema for appointment search filters."""
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    modality: Optional[str] = None
    state: Optional[str] = None
    patient_document_number: Optional[str] = None
    doctor_document_number: Optional[str] = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Page size")


class AppointmentDeleteSchema(BaseSchema):
    """Schema for appointment deletion."""
    
    event_type: EventType = Field(EventType.APPOINTMENT, description="Event type")
    action_type: ActionType = Field(ActionType.DELETE, description="Action type")
