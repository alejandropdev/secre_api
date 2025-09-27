"""API Key authentication middleware."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_api_key
from app.db.session import get_db, set_tenant_context
from app.models.api_key import ApiKey
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI
security = HTTPBearer(auto_error=False)


class TenantContext:
    """Context for storing tenant information during request processing."""
    
    def __init__(self, tenant_id: str, tenant_name: str, api_key_id: str):
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name
        self.api_key_id = api_key_id


async def get_api_key_from_header(request: Request) -> Optional[str]:
    """Extract API key from X-Api-Key header."""
    return request.headers.get("X-Api-Key")


async def verify_api_key_and_get_tenant(
    request: Request,
    api_key: str = Depends(get_api_key_from_header),
    db: AsyncSession = Depends(get_db),
) -> TenantContext:
    """Verify API key and return tenant context."""
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-Api-Key header.",
        )
    
    # Check if this is the master API key
    from app.core.config import settings
    if api_key == settings.master_api_key:
        # Master API key - create special tenant context
        tenant_context = TenantContext(
            tenant_id="master",
            tenant_name="Master Admin",
            api_key_id="master",
        )
        
        # Set tenant context in request state for RLS
        request.state.tenant_context = tenant_context
        
        # Don't set tenant context for database session (master has access to all)
        # set_tenant_context("master")  # Commented out for master access
        
        logger.info("Master API key used for request")
        return tenant_context
    
    # Hash the provided API key
    key_hash = hash_api_key(api_key)
    
    # Query database for the API key
    result = await db.execute(
        select(ApiKey, Tenant)
        .join(Tenant, ApiKey.tenant_id == Tenant.id)
        .where(
            ApiKey.key_hash == key_hash,
            ApiKey.revoked_at.is_(None),
            Tenant.is_active == True,
        )
    )
    
    result_row = result.first()
    
    if not result_row:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    api_key_obj, tenant_obj = result_row
    
    # Update last used timestamp
    api_key_obj.last_used_at = datetime.utcnow()
    await db.commit()
    
    # Create tenant context
    tenant_context = TenantContext(
        tenant_id=str(tenant_obj.id),
        tenant_name=tenant_obj.name,
        api_key_id=str(api_key_obj.id),
    )
    
    # Set tenant context in request state for RLS
    request.state.tenant_context = tenant_context
    
    # Set tenant context for database session
    set_tenant_context(str(tenant_obj.id))
    
    return tenant_context


async def get_current_tenant(
    tenant_context: TenantContext = Depends(verify_api_key_and_get_tenant),
) -> TenantContext:
    """Get current tenant context."""
    return tenant_context
