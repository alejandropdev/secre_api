"""Authentication Pydantic schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class ApiKeyCreateSchema(BaseSchema):
    """Schema for creating an API key."""
    
    name: str = Field(..., min_length=1, max_length=255, description="API key name")
    tenant_id: UUID = Field(..., description="Tenant ID")


class ApiKeyResponseSchema(BaseSchema):
    """Schema for API key responses (without sensitive data)."""
    
    id: UUID
    tenant_id: UUID
    name: str
    last_used_at: Optional[datetime] = None
    created_at: datetime
    revoked_at: Optional[datetime] = None
    
    @property
    def is_revoked(self) -> bool:
        """Check if the API key is revoked."""
        return self.revoked_at is not None


class ApiKeyCreateResponseSchema(BaseSchema):
    """Schema for API key creation response (includes plaintext key)."""
    
    api_key: ApiKeyResponseSchema
    plaintext_key: str = Field(..., description="Plaintext API key (save securely)")


class ApiKeyListResponseSchema(BaseSchema):
    """Schema for API key list responses."""
    
    api_keys: List[ApiKeyResponseSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class ApiKeyRevokeSchema(BaseSchema):
    """Schema for revoking an API key."""
    
    api_key_id: UUID = Field(..., description="API key ID to revoke")


class TenantCreateSchema(BaseSchema):
    """Schema for creating a tenant."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Tenant name")


class TenantResponseSchema(BaseSchema):
    """Schema for tenant responses."""
    
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TenantUpdateSchema(BaseSchema):
    """Schema for updating a tenant."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


class TenantListResponseSchema(BaseSchema):
    """Schema for tenant list responses."""
    
    tenants: List[TenantResponseSchema]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class TenantCreateWithApiKeyResponseSchema(BaseSchema):
    """Schema for tenant creation response that includes the API key."""
    
    tenant: TenantResponseSchema
    api_key: ApiKeyResponseSchema
    plaintext_key: str = Field(..., description="Plaintext API key (save securely)")
