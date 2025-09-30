"""Tenant-specific lookup Pydantic schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class TenantAppointmentTypeBaseSchema(BaseSchema):
    """Base schema for tenant appointment types."""
    
    code: str = Field(..., min_length=1, max_length=20, description="Unique code for the appointment type")
    name: str = Field(..., min_length=1, max_length=100, description="Display name for the appointment type")
    description: Optional[str] = Field(None, description="Optional description")
    is_active: str = Field(default="true", description="Whether the appointment type is active")


class TenantAppointmentTypeCreateSchema(TenantAppointmentTypeBaseSchema):
    """Schema for creating a tenant appointment type."""
    
    class Config:
        schema_extra = {
            "example": {
                "code": "CONSULTA_GENERAL",
                "name": "Consulta General",
                "description": "Consulta médica general de rutina",
                "is_active": "true"
            }
        }


class TenantAppointmentTypeUpdateSchema(BaseSchema):
    """Schema for updating a tenant appointment type."""
    
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[str] = Field(None, description="Whether the appointment type is active")


class TenantAppointmentTypeResponseSchema(TenantAppointmentTypeBaseSchema):
    """Schema for tenant appointment type responses."""
    
    id: int
    tenant_id: str
    created_at: str
    updated_at: str


class TenantClinicBaseSchema(BaseSchema):
    """Base schema for tenant clinics."""
    
    code: str = Field(..., min_length=1, max_length=20, description="Unique code for the clinic")
    name: str = Field(..., min_length=1, max_length=100, description="Display name for the clinic")
    description: Optional[str] = Field(None, description="Optional description")
    address: Optional[str] = Field(None, description="Clinic address")
    phone: Optional[str] = Field(None, max_length=20, description="Clinic phone number")
    email: Optional[str] = Field(None, max_length=100, description="Clinic email")
    is_active: str = Field(default="true", description="Whether the clinic is active")


class TenantClinicCreateSchema(TenantClinicBaseSchema):
    """Schema for creating a tenant clinic."""
    
    class Config:
        schema_extra = {
            "example": {
                "code": "CLINIC_001",
                "name": "Clínica Principal",
                "description": "Clínica principal del centro médico",
                "address": "Calle 123 #45-67, Bogotá",
                "phone": "+57-1-234-5678",
                "email": "info@clinica.com",
                "is_active": "true"
            }
        }


class TenantClinicUpdateSchema(BaseSchema):
    """Schema for updating a tenant clinic."""
    
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    is_active: Optional[str] = Field(None, description="Whether the clinic is active")


class TenantClinicResponseSchema(TenantClinicBaseSchema):
    """Schema for tenant clinic responses."""
    
    id: int
    tenant_id: str
    created_at: str
    updated_at: str


class TenantLookupListResponseSchema(BaseSchema):
    """Schema for tenant lookup list responses."""
    
    items: List[BaseModel]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
