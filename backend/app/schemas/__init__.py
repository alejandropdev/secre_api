"""Pydantic schemas for API contracts."""

from app.schemas.appointment import (
    AppointmentCreateSchema,
    AppointmentDeleteSchema,
    AppointmentListResponseSchema,
    AppointmentResponseSchema,
    AppointmentSearchSchema,
    AppointmentUpdateSchema,
)
from app.schemas.audit import (
    AuditLogListResponseSchema,
    AuditLogResponseSchema,
    AuditLogSearchSchema,
)
from app.schemas.auth import (
    ApiKeyCreateResponseSchema,
    ApiKeyCreateSchema,
    ApiKeyListResponseSchema,
    ApiKeyResponseSchema,
    ApiKeyRevokeSchema,
    TenantCreateSchema,
    TenantListResponseSchema,
    TenantResponseSchema,
    TenantUpdateSchema,
)
from app.schemas.base import (
    BaseSchema,
    CustomFieldsSchema,
    ErrorResponseSchema,
    TenantContextSchema,
    TimestampSchema,
)
from app.schemas.health import HealthCheckSchema, ServiceInfoSchema
from app.schemas.lookup import (
    AppointmentModalitySchema,
    AppointmentStateSchema,
    DocumentTypeSchema,
    GenderSchema,
    LookupBaseSchema,
    LookupListResponseSchema,
    LookupSearchSchema,
)
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.patient import (
    PatientCreateSchema,
    PatientDeleteSchema,
    PatientListResponseSchema,
    PatientResponseSchema,
    PatientSearchSchema,
    PatientUpdateSchema,
)

__all__ = [
    # Base schemas
    "BaseSchema",
    "CustomFieldsSchema",
    "TenantContextSchema",
    "TimestampSchema",
    "ErrorResponseSchema",
    
    # Patient schemas
    "PatientCreateSchema",
    "PatientUpdateSchema",
    "PatientResponseSchema",
    "PatientListResponseSchema",
    "PatientSearchSchema",
    "PatientDeleteSchema",
    
    # Appointment schemas
    "AppointmentCreateSchema",
    "AppointmentUpdateSchema",
    "AppointmentResponseSchema",
    "AppointmentListResponseSchema",
    "AppointmentSearchSchema",
    "AppointmentDeleteSchema",
    
    # Auth schemas
    "ApiKeyCreateSchema",
    "ApiKeyCreateResponseSchema",
    "ApiKeyResponseSchema",
    "ApiKeyListResponseSchema",
    "ApiKeyRevokeSchema",
    "TenantCreateSchema",
    "TenantResponseSchema",
    "TenantUpdateSchema",
    "TenantListResponseSchema",
    
    # Lookup schemas
    "LookupBaseSchema",
    "DocumentTypeSchema",
    "GenderSchema",
    "AppointmentModalitySchema",
    "AppointmentStateSchema",
    "LookupListResponseSchema",
    "LookupSearchSchema",
    
    # Audit schemas
    "AuditLogResponseSchema",
    "AuditLogListResponseSchema",
    "AuditLogSearchSchema",
    
    # Pagination schemas
    "PaginationParams",
    "PaginatedResponse",
    
    # Health schemas
    "HealthCheckSchema",
    "ServiceInfoSchema",
]
