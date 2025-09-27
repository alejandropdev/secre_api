#!/usr/bin/env python3
"""
Manual tenant creation script for Railway deployment.
Use this script to create tenants and API keys after deployment.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def create_tenant_manual(tenant_name: str = "Default Tenant"):
    """Create a tenant and API key manually."""
    print(f"👤 Creating tenant: {tenant_name}")
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        from app.models.tenant import Tenant
        from app.models.api_key import ApiKey
        import secrets
        import uuid
        import hashlib
        
        # Create a fresh sync engine for tenant creation
        engine = create_engine(settings.effective_database_url)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create tenant
            tenant = Tenant(
                id=uuid.uuid4(),
                name=tenant_name,
                is_active=True
            )
            session.add(tenant)
            session.flush()  # Get the tenant ID
            
            # Create API key
            api_key_value = secrets.token_hex(32)
            api_key_hash = hashlib.sha256(api_key_value.encode()).hexdigest()
            
            api_key = ApiKey(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                key_hash=api_key_hash,
                name=f"{tenant_name} API Key"
            )
            session.add(api_key)
            session.commit()
            
            print("✅ Tenant created successfully")
            print(f"   Tenant ID: {tenant.id}")
            print(f"   Tenant Name: {tenant.name}")
            print(f"   API Key: {api_key_value}")
            print("   🔐 Keep this API key safe - you'll need it to access the API!")
            return True
            
    except Exception as e:
        print(f"❌ Tenant creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("🚀 Manual Tenant Creation Script")
    print("=" * 40)
    
    # Get tenant name from command line or use default
    tenant_name = sys.argv[1] if len(sys.argv) > 1 else "Default Tenant"
    
    if create_tenant_manual(tenant_name):
        print("\n🎉 Tenant creation completed successfully!")
        print("\nYou can now use this API key to make authenticated requests to your API.")
    else:
        print("\n❌ Tenant creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

