"""Admin endpoints for initial setup."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import ApiKeyCreateResponseSchema, TenantCreateSchema
from app.services.api_key_service import ApiKeyService
from app.services.tenant_service import TenantService
from app.utils.schema_conversion import convert_api_keys_to_response_list

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/admin", tags=["Admin"])


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
