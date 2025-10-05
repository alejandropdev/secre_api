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
    modality_id: int = Field(
        ..., 
        description="ID de la modalidad de la cita",
        example=1
    )
    state_id: int = Field(
        ..., 
        description="ID del estado de la cita",
        example=1
    )
    notification_state: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Estado de notificación (pending, sent, failed)",
        example="pending"
    )
    appointment_type_id: Optional[int] = Field(
        None, 
        description="ID del tipo de cita específico del inquilino",
        example=1
    )
    clinic_id: Optional[int] = Field(
        None, 
        description="ID de la clínica específica del inquilino",
        example=1
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
        json_schema_extra = {
            "example": {
                "startAppointment": "2024-01-15T10:00:00-05:00",
                "endAppointment": "2024-01-15T11:00:00-05:00",
                "patientDocumentTypeId": 1,
                "patientDocumentNumber": "12345678",
                "doctorDocumentTypeId": 1,
                "doctorDocumentNumber": "87654321",
                "modalityId": 1,
                "stateId": 1,
                "notificationState": "pending",
                "appointmentTypeId": 1,
                "clinicId": 1,
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
    modality_id: Optional[int] = None
    state_id: Optional[int] = None
    notification_state: Optional[str] = Field(None, max_length=50)
    appointment_type_id: Optional[int] = None
    clinic_id: Optional[int] = None
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
    modality_name: Optional[str] = Field(None, description="Name of the appointment modality")
    state_name: Optional[str] = Field(None, description="Name of the appointment state")
    appointment_type_name: Optional[str] = Field(None, description="Name of the appointment type")
    clinic_name: Optional[str] = Field(None, description="Name of the clinic")


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
    modality_id: Optional[int] = None
    state_id: Optional[int] = None
    patient_document_number: Optional[str] = None
    doctor_document_number: Optional[str] = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Page size")


class AppointmentDeleteSchema(BaseSchema):
    """Schema for appointment deletion."""


class SimpleAppointmentCreateSchema(BaseSchema):
    """Simplified schema for creating an appointment."""
    
    start_datetime: str = Field(..., description="Start datetime in ISO format. If no timezone is specified, assumes UTC (e.g., 2024-01-15T10:00:00 or 2024-01-15T10:00:00Z)")
    end_datetime: str = Field(..., description="End datetime in ISO format. If no timezone is specified, assumes UTC (e.g., 2024-01-15T11:00:00 or 2024-01-15T11:00:00Z)")
    patient_document_type_id: int = Field(..., description="Patient document type ID")
    patient_document_number: str = Field(..., description="Patient document number")
    doctor_document_type_id: int = Field(..., description="Doctor document type ID")
    doctor_document_number: str = Field(..., description="Doctor document number")
    modality_id: int = Field(..., description="Appointment modality ID")
    state_id: int = Field(..., description="Appointment state ID")
    appointment_type_id: Optional[int] = Field(None, description="Appointment type ID")
    clinic_id: Optional[int] = Field(None, description="Clinic ID")
    comment: Optional[str] = Field(None, description="Appointment comment")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('start_datetime', 'end_datetime')
    def validate_datetime(cls, v):
        """Validate datetime format and convert to UTC."""
        try:
            from datetime import datetime
            import pytz
            
            # Parse the datetime string
            if v.endswith('Z'):
                # UTC timezone
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            elif '+' in v or v.count('-') > 2:
                # Has timezone info
                dt = datetime.fromisoformat(v)
            else:
                # No timezone info - assume it's local time and convert to UTC
                # For now, we'll assume it's UTC to maintain backward compatibility
                # In production, you might want to get the timezone from tenant settings
                dt = datetime.fromisoformat(v)
                # Mark as UTC
                dt = dt.replace(tzinfo=pytz.UTC)
            
            return dt
        except ValueError:
            raise ValueError(f"Invalid datetime format: {v}. Use ISO format like '2024-01-15T10:00:00' or '2024-01-15T10:00:00Z'")
    
    @validator('custom_fields')
    def validate_custom_fields(cls, v):
        """Validate custom fields."""
        if v is not None:
            return EnhancedValidators.validate_custom_fields(cls, v)
        return v
