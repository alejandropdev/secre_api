"""Lookup/reference data Pydantic schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class LookupBaseSchema(BaseSchema):
    """Base schema for lookup tables."""
    
    id: int
    code: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


class DocumentTypeSchema(LookupBaseSchema):
    """Schema for document types."""
    
    pass


class GenderSchema(LookupBaseSchema):
    """Schema for genders."""
    
    pass


class AppointmentModalitySchema(LookupBaseSchema):
    """Schema for appointment modalities."""
    
    pass


class AppointmentStateSchema(LookupBaseSchema):
    """Schema for appointment states."""
    
    pass


class LookupListResponseSchema(BaseSchema):
    """Schema for lookup list responses."""
    
    items: List[LookupBaseSchema]
    total: int


class LookupSearchSchema(BaseSchema):
    """Schema for lookup search filters."""
    
    code: Optional[str] = None
    name: Optional[str] = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Page size")
