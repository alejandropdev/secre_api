"""Tenant service for managing multi-tenant data."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


class TenantService:
    """Service for managing tenants."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_tenant(self, name: str) -> Tenant:
        """Create a new tenant."""
        tenant = Tenant(name=name, is_active=True)
        
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        
        logger.info(f"Created tenant: {name}")
        
        return tenant
    
    async def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tenant_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants."""
        result = await self.db.execute(
            select(Tenant).order_by(Tenant.created_at.desc())
        )
        return result.scalars().all()
    
    async def update_tenant(self, tenant_id: UUID, name: Optional[str] = None, is_active: Optional[bool] = None) -> Optional[Tenant]:
        """Update tenant information."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return None
        
        if name is not None:
            tenant.name = name
        if is_active is not None:
            tenant.is_active = is_active
        
        await self.db.commit()
        await self.db.refresh(tenant)
        
        logger.info(f"Updated tenant {tenant_id}")
        
        return tenant
    
    async def deactivate_tenant(self, tenant_id: UUID) -> bool:
        """Deactivate a tenant."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return False
        
        tenant.is_active = False
        await self.db.commit()
        
        logger.info(f"Deactivated tenant {tenant_id}")
        
        return True
