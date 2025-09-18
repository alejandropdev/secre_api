"""Patient Pydantic schemas matching client payloads."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import ActionType, BaseSchema, CustomFieldsSchema, EventType
from app.schemas.validators import EnhancedValidators


class PatientBaseSchema(BaseSchema):
    """Base patient schema with common fields."""
    
    first_name: str = Field(..., min_length=1, max_length=255, description="First name")
    second_name: Optional[str] = Field(None, max_length=255, description="Second name")
    first_last_name: str = Field(..., min_length=1, max_length=255, description="First last name")
    second_last_name: Optional[str] = Field(None, max_length=255, description="Second last name")
    birth_date: date = Field(..., description="Birth date")
    gender_id: int = Field(..., description="Gender ID")
    document_type_id: int = Field(..., description="Document type ID")
    document_number: str = Field(..., min_length=1, max_length=50, description="Document number")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    cell_phone: Optional[str] = Field(None, max_length=20, description="Cell phone number")
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    eps_id: Optional[str] = Field(None, max_length=100, description="Health insurance provider ID")
    habeas_data: bool = Field(False, description="Habeas data consent")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom tenant-specific fields")


class PatientCreateSchema(PatientBaseSchema):
    """Schema for creating a patient (matches client payload)."""
    
    event_type: EventType = Field(EventType.PATIENT, description="Event type")
    action_type: ActionType = Field(ActionType.CREATE, description="Action type")
    
    @validator('document_number')
    def validate_document_number(cls, v, values):
        """Validate document number based on document type."""
        return EnhancedValidators.validate_document_number(cls, v, values)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        return EnhancedValidators.validate_phone(cls, v)
    
    @validator('cell_phone')
    def validate_cell_phone(cls, v):
        """Validate cell phone number format."""
        return EnhancedValidators.validate_cell_phone(cls, v)
    
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
    
    event_type: EventType = Field(EventType.PATIENT, description="Event type")
    action_type: ActionType = Field(ActionType.UPDATE, description="Action type")
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    second_name: Optional[str] = Field(None, max_length=255)
    first_last_name: Optional[str] = Field(None, min_length=1, max_length=255)
    second_last_name: Optional[str] = Field(None, max_length=255)
    birth_date: Optional[date] = None
    gender_id: Optional[int] = None
    document_type_id: Optional[int] = None
    document_number: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    cell_phone: Optional[str] = Field(None, max_length=20)
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
    
    @validator('cell_phone')
    def validate_cell_phone(cls, v):
        """Validate cell phone number format."""
        if v is not None:
            return EnhancedValidators.validate_cell_phone(cls, v)
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
    
    id: UUID
    tenant_id: UUID
    created_at: str
    updated_at: str


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
    cell_phone: Optional[str] = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Page size")


class PatientDeleteSchema(BaseSchema):
    """Schema for patient deletion."""
    
    event_type: EventType = Field(EventType.PATIENT, description="Event type")
    action_type: ActionType = Field(ActionType.DELETE, description="Action type")
