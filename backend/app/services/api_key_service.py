"""API Key service for managing authentication keys."""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_api_key, hash_api_key
from app.models.api_key import ApiKey
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


class ApiKeyService:
    """Service for managing API keys."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_api_key(
        self,
        tenant_id: UUID,
        name: str,
    ) -> tuple[str, ApiKey]:
        """Create a new API key for a tenant.
        
        Returns:
            Tuple of (plaintext_key, api_key_model)
        """
        # Generate new API key
        plaintext_key = generate_api_key()
        key_hash = hash_api_key(plaintext_key)
        
        # Create API key record
        api_key = ApiKey(
            tenant_id=tenant_id,
            key_hash=key_hash,
            name=name,
        )
        
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        
        logger.info(f"Created API key for tenant {tenant_id}: {name}")
        
        return plaintext_key, api_key
    
    async def get_api_key_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        """Get API key by its hash."""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash)
        )
        return result.scalar_one_or_none()
    
    async def get_api_keys_by_tenant(self, tenant_id: UUID) -> List[ApiKey]:
        """Get all API keys for a tenant."""
        result = await self.db.execute(
            select(ApiKey)
            .where(ApiKey.tenant_id == tenant_id)
            .order_by(ApiKey.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_all_api_keys(self) -> List[ApiKey]:
        """Get all API keys across all tenants (master API key only)."""
        result = await self.db.execute(
            select(ApiKey)
            .order_by(ApiKey.created_at.desc())
        )
        return result.scalars().all()
    
    async def revoke_api_key(self, api_key_id: UUID) -> bool:
        """Revoke an API key."""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.id == api_key_id)
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            return False
        
        api_key.revoked_at = datetime.utcnow()
        await self.db.commit()
        
        logger.info(f"Revoked API key {api_key_id}")
        return True
    
    async def update_last_used(self, api_key_id: UUID) -> None:
        """Update the last used timestamp for an API key."""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.id == api_key_id)
        )
        api_key = result.scalar_one_or_none()
        
        if api_key:
            api_key.last_used_at = datetime.utcnow()
            await self.db.commit()
