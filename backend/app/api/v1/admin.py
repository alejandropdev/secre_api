"""Admin endpoints for initial setup."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    ApiKeyCreateResponseSchema, 
    TenantCreateSchema, 
    TenantCreateWithApiKeyResponseSchema
)
from app.services.api_key_service import ApiKeyService
from app.services.tenant_service import TenantService
from app.utils.schema_conversion import convert_api_keys_to_response_list, convert_tenants_to_response_list

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/admin", tags=["Admin"])


def verify_master_api_key(x_api_key: str = Header(..., alias="X-Api-Key")):
    """Verify master API key for admin operations."""
    if x_api_key != settings.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid master API key"
        )
    return x_api_key


@router.post("/bootstrap", response_model=ApiKeyCreateResponseSchema, status_code=status.HTTP_201_CREATED)
async def bootstrap_tenant_and_api_key(
    tenant_data: TenantCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Bootstrap the first tenant and API key (no authentication required)."""
    
    tenant_service = TenantService(db)
    api_key_service = ApiKeyService(db)
    
    # Check if any tenants already exist
    existing_tenants = await tenant_service.get_all_tenants()
    if existing_tenants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System already bootstrapped. Use regular auth endpoints."
        )
    
    # Create tenant
    tenant = await tenant_service.create_tenant(tenant_data.name)
    
    # Create API key for the tenant
    plaintext_key, api_key = await api_key_service.create_api_key(
        tenant_id=tenant.id,
        name="Bootstrap API Key",
    )
    
    logger.info(f"Bootstrapped tenant {tenant.name} with API key {api_key.id}")
    
    return ApiKeyCreateResponseSchema(
        api_key=convert_api_keys_to_response_list([api_key])[0],
        plaintext_key=plaintext_key,
    )


@router.post("/tenants", response_model=TenantCreateWithApiKeyResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_tenant_with_api_key(
    tenant_data: TenantCreateSchema,
    db: AsyncSession = Depends(get_db),
    master_key: str = Depends(verify_master_api_key),
):
    """Create a new tenant with automatic API key generation (master API key required)."""
    
    tenant_service = TenantService(db)
    api_key_service = ApiKeyService(db)
    
    # Check if tenant name already exists
    existing_tenant = await tenant_service.get_tenant_by_name(tenant_data.name)
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this name already exists"
        )
    
    # Create tenant
    tenant = await tenant_service.create_tenant(tenant_data.name)
    
    # Create API key for the tenant
    plaintext_key, api_key = await api_key_service.create_api_key(
        tenant_id=tenant.id,
        name=f"{tenant.name} - Primary API Key",
    )
    
    logger.info(f"Created tenant {tenant.name} with API key {api_key.id} using master key")
    
    return TenantCreateWithApiKeyResponseSchema(
        tenant=convert_tenants_to_response_list([tenant])[0],
        api_key=convert_api_keys_to_response_list([api_key])[0],
        plaintext_key=plaintext_key,
    )
