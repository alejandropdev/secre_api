"""Appointment Pydantic schemas matching client payloads."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema
from app.schemas.validators import EnhancedValidators


class AppointmentBaseSchema(BaseSchema):
    """Base appointment schema with common fields."""
    
    start_utc: datetime = Field(
        ..., 
        description="Hora de inicio de la cita en UTC",
        example="2024-01-15T15:00:00Z"
    )
    end_utc: datetime = Field(
        ..., 
        description="Hora de finalización de la cita en UTC",
        example="2024-01-15T16:00:00Z"
    )
    patient_document_type_id: int = Field(
        ..., 
        description="ID del tipo de documento del paciente",
        example=1
    )
    patient_document_number: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Número de documento del paciente",
        example="12345678"
    )
    doctor_document_type_id: int = Field(
        ..., 
        description="ID del tipo de documento del médico",
        example=1
    )
    doctor_document_number: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Número de documento del médico",
        example="87654321"
    )
    modality: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Modalidad de la cita (presencial, virtual, telemedicina, domicilio)",
        example="presencial"
    )
    state: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Estado de la cita (scheduled, confirmed, cancelled, completed)",
        example="scheduled"
    )
    notification_state: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Estado de notificación (pending, sent, failed)",
        example="pending"
    )
    appointment_type: Optional[str] = Field(
        None, 
        max_length=100, 
        description="Tipo de cita (consulta_general, especialista, control, urgencia)",
        example="consulta_general"
    )
    clinic_id: Optional[str] = Field(
        None, 
        max_length=100, 
        description="ID de la clínica o consultorio",
        example="CLINIC001"
    )
    comment: Optional[str] = Field(
        None, 
        description="Comentarios adicionales sobre la cita",
        example="Consulta de rutina - paciente alérgico a penicilina"
    )
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Campos personalizados específicos del inquilino para información adicional de la cita",
        example={
            "room": "A101",
            "specialInstructions": "Paciente alérgico a penicilina",
            "insurance": {
                "provider": "EPS001",
                "policyNumber": "POL123456"
            }
        }
    )


class AppointmentCreateSchema(AppointmentBaseSchema):
    """Schema for creating an appointment (matches client payload)."""
    
    # RFC3339 format fields for client compatibility
    start_appointment: str = Field(
        ..., 
        description="Hora de inicio de la cita en formato RFC3339 con zona horaria",
        example="2024-01-15T10:00:00-05:00"
    )
    end_appointment: str = Field(
        ..., 
        description="Hora de finalización de la cita en formato RFC3339 con zona horaria",
        example="2024-01-15T11:00:00-05:00"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "startAppointment": "2024-01-15T10:00:00-05:00",
                "endAppointment": "2024-01-15T11:00:00-05:00",
                "patientDocumentTypeId": 1,
                "patientDocumentNumber": "12345678",
                "doctorDocumentTypeId": 1,
                "doctorDocumentNumber": "87654321",
                "modality": "presencial",
                "state": "scheduled",
                "notificationState": "pending",
                "appointmentType": "consulta_general",
                "clinicId": "CLINIC001",
                "comment": "Consulta de rutina - paciente alérgico a penicilina",
                "customFields": {
                    "room": "A101",
                    "specialInstructions": "Paciente alérgico a penicilina",
                    "insurance": {
                        "provider": "EPS001",
                        "policyNumber": "POL123456"
                    }
                }
            }
        }
    
    @validator('start_appointment', 'end_appointment')
    def validate_rfc3339_datetime(cls, v):
        """Validate RFC3339 datetime format."""
        return EnhancedValidators.validate_rfc3339_datetime(cls, v)
    
    @validator('end_utc')
    def validate_appointment_datetime(cls, v, values):
        """Validate appointment datetime constraints."""
        return EnhancedValidators.validate_appointment_datetime(cls, v, values)
    
    @validator('custom_fields')
    def validate_custom_fields(cls, v):
        """Validate custom fields."""
        return EnhancedValidators.validate_custom_fields(cls, v)


class AppointmentUpdateSchema(BaseSchema):
    """Schema for updating an appointment."""
    
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
        if v is not None:
            return EnhancedValidators.validate_rfc3339_datetime(cls, v)
        return v
    
    @validator('end_utc')
    def validate_appointment_datetime(cls, v, values):
        """Validate appointment datetime constraints."""
        if v is not None and 'start_utc' in values and values['start_utc']:
            return EnhancedValidators.validate_appointment_datetime(cls, v, values)
        return v
    
    @validator('custom_fields')
    def validate_custom_fields(cls, v):
        """Validate custom fields."""
        if v is not None:
            return EnhancedValidators.validate_custom_fields(cls, v)
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


class SimpleAppointmentCreateSchema(BaseSchema):
    """Simplified schema for creating an appointment."""
    
    start_datetime: str = Field(..., description="Start datetime in ISO format (e.g., 2024-01-15T10:00:00)")
    end_datetime: str = Field(..., description="End datetime in ISO format (e.g., 2024-01-15T11:00:00)")
    patient_document_type_id: int = Field(..., description="Patient document type ID")
    patient_document_number: str = Field(..., description="Patient document number")
    doctor_document_type_id: int = Field(..., description="Doctor document type ID")
    doctor_document_number: str = Field(..., description="Doctor document number")
    modality: str = Field(default="presencial", description="Appointment modality")
    state: str = Field(default="scheduled", description="Appointment state")
    appointment_type: str = Field(default="consulta", description="Appointment type")
    clinic_id: Optional[str] = Field(None, description="Clinic ID")
    comment: Optional[str] = Field(None, description="Appointment comment")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('start_datetime', 'end_datetime')
    def validate_datetime(cls, v):
        """Validate datetime format."""
        try:
            from datetime import datetime
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid datetime format: {v}. Use ISO format like '2024-01-15T10:00:00'")
    
    @validator('custom_fields')
    def validate_custom_fields(cls, v):
        """Validate custom fields."""
        if v is not None:
            return EnhancedValidators.validate_custom_fields(cls, v)
        return v
