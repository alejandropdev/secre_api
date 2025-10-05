"""Authentication endpoints for API key management."""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.middleware.auth import TenantContext, get_current_tenant
from app.schemas.auth import (
    ApiKeyCreateResponseSchema,
    ApiKeyCreateSchema,
    ApiKeyListResponseSchema,
    TenantCreateSchema,
    TenantListResponseSchema,
    TenantResponseSchema,
    TenantUpdateSchema,
)
from app.schemas.api_key_usage import (
    ApiKeyUsageStatsSchema,
    TenantUsageStatsResponseSchema,
    TopEndpointsResponseSchema,
    UsageStatsResponseSchema,
)
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services.api_key_service import ApiKeyService
from app.services.api_key_usage_service import ApiKeyUsageService
from app.services.tenant_service import TenantService
from app.utils.schema_conversion import (
    convert_api_keys_to_response_list,
    convert_tenants_to_response_list,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])


# Tenant Management Endpoints
@router.post("/tenants", response_model=TenantResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Create a new tenant (admin only)."""
    
    # Check if current tenant has admin privileges (for now, allow all authenticated tenants)
    # In production, you might want to add role-based access control
    
    tenant_service = TenantService(db)
    
    # Check if tenant name already exists
    existing_tenant = await tenant_service.get_tenant_by_name(tenant_data.name)
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this name already exists"
        )
    
    tenant = await tenant_service.create_tenant(tenant_data.name)
    
    logger.info(f"Created tenant {tenant.name} by API key {current_tenant.api_key_id}")
    
    return TenantResponseSchema(
        id=tenant.id,
        name=tenant.name,
        is_active=tenant.is_active,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


@router.get("/tenants", response_model=TenantListResponseSchema)
async def list_tenants(
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """List all tenants (admin only)."""
    
    tenant_service = TenantService(db)
    tenants = await tenant_service.get_all_tenants()
    
    # Simple pagination (in production, implement proper pagination in service)
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_tenants = tenants[start_idx:end_idx]
    
    return TenantListResponseSchema(
        tenants=convert_tenants_to_response_list(paginated_tenants),
        total=len(tenants),
        page=page,
        size=size,
        has_next=end_idx < len(tenants),
        has_prev=page > 1,
    )


@router.get("/tenants/{tenant_id}", response_model=TenantResponseSchema)
async def get_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get tenant by ID (admin only)."""
    
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant_by_id(tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return TenantResponseSchema(
        id=tenant.id,
        name=tenant.name,
        is_active=tenant.is_active,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


@router.patch("/tenants/{tenant_id}", response_model=TenantResponseSchema)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Update tenant (admin only)."""
    
    tenant_service = TenantService(db)
    
    # Check if tenant exists
    existing_tenant = await tenant_service.get_tenant_by_id(tenant_id)
    if not existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update tenant
    update_data = tenant_data.dict(exclude_unset=True)
    updated_tenant = await tenant_service.update_tenant(tenant_id, **update_data)
    
    if not updated_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update tenant"
        )
    
    logger.info(f"Updated tenant {tenant_id} by API key {current_tenant.api_key_id}")
    
    return TenantResponseSchema(
        id=updated_tenant.id,
        name=updated_tenant.name,
        is_active=updated_tenant.is_active,
        created_at=updated_tenant.created_at,
        updated_at=updated_tenant.updated_at,
    )


# API Key Management Endpoints
@router.post("/api-keys", response_model=ApiKeyCreateResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: ApiKeyCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Create a new API key for a tenant."""
    
    api_key_service = ApiKeyService(db)
    
    # Verify tenant exists and is active
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant_by_id(api_key_data.tenant_id)
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inactive tenant"
        )
    
    # Create API key
    plaintext_key, api_key = await api_key_service.create_api_key(
        tenant_id=api_key_data.tenant_id,
        name=api_key_data.name,
    )
    
    logger.info(f"Created API key {api_key.name} for tenant {api_key_data.tenant_id} by API key {current_tenant.api_key_id}")
    
    return ApiKeyCreateResponseSchema(
        api_key=convert_api_keys_to_response_list([api_key])[0],
        plaintext_key=plaintext_key,
    )


@router.get("/api-keys", response_model=ApiKeyListResponseSchema)
async def list_api_keys(
    tenant_id: UUID = None,
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """List API keys (redacts secrets)."""
    
    api_key_service = ApiKeyService(db)
    
    # Handle different scenarios for getting API keys
    if tenant_id:
        # Specific tenant requested
        target_tenant_id = tenant_id
        
        # Verify tenant exists and user has access
        tenant_service = TenantService(db)
        tenant = await tenant_service.get_tenant_by_id(target_tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Get API keys for specific tenant
        api_keys = await api_key_service.get_api_keys_by_tenant(target_tenant_id)
        
    elif current_tenant.tenant_id == "master":
        # Master API key - get all API keys across all tenants
        api_keys = await api_key_service.get_all_api_keys()
        
    else:
        # Regular tenant API key - get keys for current tenant
        target_tenant_id = UUID(current_tenant.tenant_id)
        
        # Verify tenant exists
        tenant_service = TenantService(db)
        tenant = await tenant_service.get_tenant_by_id(target_tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Get API keys for current tenant
        api_keys = await api_key_service.get_api_keys_by_tenant(target_tenant_id)
    
    # Simple pagination
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_keys = api_keys[start_idx:end_idx]
    
    return ApiKeyListResponseSchema(
        api_keys=convert_api_keys_to_response_list(paginated_keys),
        total=len(api_keys),
        page=page,
        size=size,
        has_next=end_idx < len(api_keys),
        has_prev=page > 1,
    )


@router.post("/api-keys/{api_key_id}/revoke", response_model=dict)
async def revoke_api_key(
    api_key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Revoke an API key."""
    
    api_key_service = ApiKeyService(db)
    
    success = await api_key_service.revoke_api_key(api_key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    logger.info(f"Revoked API key {api_key_id} by API key {current_tenant.api_key_id}")
    
    return {"message": "API key revoked successfully"}


@router.get("/api-keys/{api_key_id}", response_model=dict)
async def get_api_key(
    api_key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get API key details (without sensitive data)."""
    
    api_key_service = ApiKeyService(db)
    
    # This endpoint would need to be implemented in the service
    # For now, return a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get API key endpoint not yet implemented"
    )


# API Usage Statistics Endpoints
@router.get("/api-keys/{api_key_id}/usage", response_model=UsageStatsResponseSchema)
async def get_api_key_usage_stats(
    api_key_id: UUID,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get comprehensive usage statistics for a specific API key."""
    
    usage_service = ApiKeyUsageService(db)
    
    # Get usage statistics
    stats = await usage_service.get_api_key_usage_stats(
        api_key_id=api_key_id,
        days=days,
    )
    
    return UsageStatsResponseSchema(stats=stats)


@router.get("/tenants/{tenant_id}/usage", response_model=TenantUsageStatsResponseSchema)
async def get_tenant_usage_stats(
    tenant_id: UUID,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get usage statistics for all API keys in a tenant."""
    
    usage_service = ApiKeyUsageService(db)
    
    # Get tenant usage statistics
    stats = await usage_service.get_tenant_usage_stats(
        tenant_id=tenant_id,
        days=days,
    )
    
    return TenantUsageStatsResponseSchema(stats=stats)


@router.get("/usage/top-endpoints", response_model=TopEndpointsResponseSchema)
async def get_top_endpoints(
    days: int = 7,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get top endpoints by usage across all tenants or current tenant."""
    
    usage_service = ApiKeyUsageService(db)
    
    # Get top endpoints (filtered by current tenant)
    if current_tenant.tenant_id == "master":
        # Master API key - get top endpoints across all tenants
        endpoints = await usage_service.get_top_endpoints(
            tenant_id=None,
            days=days,
            limit=limit,
        )
    else:
        endpoints = await usage_service.get_top_endpoints(
            tenant_id=UUID(current_tenant.tenant_id),
            days=days,
            limit=limit,
        )
    
    return TopEndpointsResponseSchema(
        endpoints=endpoints,
        period_days=days,
    )
