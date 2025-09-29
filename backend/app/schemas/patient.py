"""Patient Pydantic schemas matching client payloads."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema, CustomFieldsSchema
from app.schemas.validators import EnhancedValidators


class PatientBaseSchema(BaseSchema):
    """Base patient schema with common fields."""
    
    first_name: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Primer nombre del paciente",
        example="Juan"
    )
    second_name: Optional[str] = Field(
        None, 
        max_length=255, 
        description="Segundo nombre del paciente (opcional)",
        example="Carlos"
    )
    first_last_name: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Primer apellido del paciente",
        example="Pérez"
    )
    second_last_name: Optional[str] = Field(
        None, 
        max_length=255, 
        description="Segundo apellido del paciente (opcional)",
        example="González"
    )
    birth_date: Optional[date] = Field(
        None, 
        description="Fecha de nacimiento del paciente en formato YYYY-MM-DD",
        example="1990-05-15"
    )
    gender_id: Optional[int] = Field(
        None, 
        description="ID del género del paciente (1: Masculino, 2: Femenino, 3: Otro)",
        example=1
    )
    document_type_id: int = Field(
        ..., 
        description="ID del tipo de documento de identidad (1: Cédula, 2: Pasaporte, 3: Tarjeta de identidad)",
        example=1
    )
    document_number: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Número de documento de identidad del paciente",
        example="12345678"
    )
    phone: str = Field(
        ..., 
        max_length=20, 
        description="Número de teléfono del paciente",
        example="+57-300-123-4567"
    )
    email: str = Field(
        ..., 
        max_length=255, 
        description="Dirección de correo electrónico del paciente",
        example="juan.perez@example.com"
    )
    eps_id: Optional[str] = Field(
        None, 
        max_length=100, 
        description="ID de la EPS (Entidad Promotora de Salud) del paciente",
        example="EPS001"
    )
    habeas_data: bool = Field(
        False, 
        description="Consentimiento para el tratamiento de datos personales (Ley 1581 de 2012)",
        example=True
    )
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Campos personalizados específicos del inquilino para información adicional del paciente",
        example={
            "emergencyContact": "María González",
            "emergencyPhone": "+57-300-987-6543",
            "allergies": ["penicilina", "aspirina"],
            "medicalHistory": {
                "diabetes": True,
                "hypertension": False,
                "lastCheckup": "2023-12-01"
            }
        }
    )


class PatientCreateSchema(PatientBaseSchema):
    """Schema for creating a patient (matches client payload)."""
    
    class Config:
        schema_extra = {
            "example": {
                "firstName": "Juan",
                "secondName": "Carlos",
                "firstLastName": "Pérez",
                "secondLastName": "González",
                "birthDate": "1990-05-15",
                "genderId": 1,
                "documentTypeId": 1,
                "documentNumber": "12345678",
                "phone": "+57-1-234-5678",
                "email": "juan.perez@example.com",
                "epsId": "EPS001",
                "habeasData": True,
                "customFields": {
                    "emergencyContact": "María González",
                    "emergencyPhone": "+57-300-987-6543",
                    "allergies": ["penicilina", "aspirina"],
                    "medicalHistory": {
                        "diabetes": True,
                        "hypertension": False,
                        "lastCheckup": "2023-12-01"
                    }
                }
            }
        }
    
    @validator('document_number')
    def validate_document_number(cls, v, values):
        """Validate document number based on document type."""
        return EnhancedValidators.validate_document_number(cls, v, values)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        return EnhancedValidators.validate_phone(cls, v)
    
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        return EnhancedValidators.validate_email(cls, v)
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        """Validate birth date."""
        return EnhancedValidators.validate_birth_date(cls, v)
    
    @validator('custom_fields')
    def validate_custom_fields(cls, v):
        """Validate custom fields."""
        return EnhancedValidators.validate_custom_fields(cls, v)


class PatientUpdateSchema(BaseSchema):
    """Schema for updating a patient."""
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    second_name: Optional[str] = Field(None, max_length=255)
    first_last_name: Optional[str] = Field(None, min_length=1, max_length=255)
    second_last_name: Optional[str] = Field(None, max_length=255)
    birth_date: Optional[date] = None
    gender_id: Optional[int] = None
    document_type_id: Optional[int] = None
    document_number: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    eps_id: Optional[str] = Field(None, max_length=100)
    habeas_data: Optional[bool] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is not None:
            return EnhancedValidators.validate_phone(cls, v)
        return v
    
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if v is not None:
            return EnhancedValidators.validate_email(cls, v)
        return v
    
    @validator('custom_fields')
    def validate_custom_fields(cls, v):
        """Validate custom fields."""
        if v is not None:
            return EnhancedValidators.validate_custom_fields(cls, v)
        return v


class PatientResponseSchema(PatientBaseSchema):
    """Schema for patient responses."""
    
    id: UUID = Field(..., description="ID único del paciente", example="550e8400-e29b-41d4-a716-446655440000")
    tenant_id: UUID = Field(..., description="ID del inquilino propietario del paciente", example="550e8400-e29b-41d4-a716-446655440001")
    created_at: str = Field(..., description="Fecha y hora de creación en formato ISO 8601 UTC", example="2024-01-15T10:30:00Z")
    updated_at: str = Field(..., description="Fecha y hora de última actualización en formato ISO 8601 UTC", example="2024-01-15T10:30:00Z")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tenantId": "550e8400-e29b-41d4-a716-446655440001",
                "firstName": "Juan",
                "secondName": "Carlos",
                "firstLastName": "Pérez",
                "secondLastName": "González",
                "birthDate": "1990-05-15",
                "genderId": 1,
                "documentTypeId": 1,
                "documentNumber": "12345678",
                "phone": "+57-1-234-5678",
                "email": "juan.perez@example.com",
                "epsId": "EPS001",
                "habeasData": True,
                "customFields": {
                    "emergencyContact": "María González",
                    "emergencyPhone": "+57-300-987-6543",
                    "allergies": ["penicilina", "aspirina"],
                    "medicalHistory": {
                        "diabetes": True,
                        "hypertension": False,
                        "lastCheckup": "2023-12-01"
                    }
                },
                "createdAt": "2024-01-15T10:30:00Z",
                "updatedAt": "2024-01-15T10:30:00Z"
            }
        }


class PatientListResponseSchema(BaseSchema):
    """Schema for patient list responses."""
    
    patients: List[PatientResponseSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class PatientSearchSchema(BaseSchema):
    """Schema for patient search filters."""
    
    document_type_id: Optional[int] = None
    document_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Page size")


class PatientDeleteSchema(BaseSchema):
    """Schema for patient deletion."""


class SimplePatientCreateSchema(BaseSchema):
    """Simplified schema for creating a patient."""
    
    first_name: str = Field(..., min_length=1, max_length=255)
    first_last_name: str = Field(..., min_length=1, max_length=255)
    document_type_id: int = Field(...)
    document_number: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=255)
    second_name: Optional[str] = Field(None, max_length=255)
    second_last_name: Optional[str] = Field(None, max_length=255)
    birth_date: Optional[date] = Field(None)
    gender_id: Optional[int] = Field(None)
    eps_id: Optional[str] = Field(None, max_length=100)
    habeas_data: bool = Field(False)
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        return EnhancedValidators.validate_phone(cls, v)
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        return EnhancedValidators.validate_email(cls, v)
    
    @validator('document_number')
    def validate_document_number(cls, v, values):
        """Validate document number based on document type."""
        return EnhancedValidators.validate_document_number(cls, v, values)
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        """Validate birth date."""
        return EnhancedValidators.validate_birth_date(cls, v)
    
    @validator('custom_fields')
    def validate_custom_fields(cls, v):
        """Validate custom fields."""
        if v is not None:
            return EnhancedValidators.validate_custom_fields(cls, v)
        return v
