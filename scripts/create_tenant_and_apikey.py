#!/usr/bin/env python3
"""Script to create demo tenant and API key."""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.api_key_service import ApiKeyService
from app.services.tenant_service import TenantService


async def create_demo_data():
    """Create demo tenant and API key."""
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
    )
    
    # Create session factory
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with AsyncSessionLocal() as db:
        # Create tenant service
        tenant_service = TenantService(db)
        
        # Create demo tenant
        print("Creating demo tenant...")
        tenant = await tenant_service.create_tenant("Demo Medical Center")
        print(f"Created tenant: {tenant.name} (ID: {tenant.id})")
        
        # Create API key service
        api_key_service = ApiKeyService(db)
        
        # Create demo API key
        print("Creating demo API key...")
        plaintext_key, api_key = await api_key_service.create_api_key(
            tenant_id=tenant.id,
            name="Demo API Key"
        )
        
        print(f"Created API key: {api_key.name} (ID: {api_key.id})")
        print(f"API Key (save this securely): {plaintext_key}")
        print(f"API Key Hash: {api_key.key_hash}")
        
        print("\nDemo data created successfully!")
        print(f"Use this API key in the X-Api-Key header: {plaintext_key}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_demo_data())
