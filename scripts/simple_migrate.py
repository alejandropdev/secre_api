#!/usr/bin/env python3
"""
Simple migration script for Railway deployment.
This script runs migrations using the sync engine directly.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def run_migrations():
    """Run database migrations using alembic."""
    print("🔄 Running database migrations...")
    
    try:
        from alembic.config import Config
        from alembic import command
        from app.core.config import settings
        
        # Get the database URL
        db_url = settings.effective_database_url
        print(f"Using database URL: {db_url[:30]}...")
        
        # Set up Alembic configuration
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", str(Path(__file__).parent.parent / "alembic"))
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        # Run migrations
        # Force sync mode for Railway deployment
        os.environ["ALEMBIC_SYNC_MODE"] = "true"
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def seed_data():
    """Seed initial lookup data."""
    print("🌱 Seeding initial data...")
    
    try:
        # The seeding data is already included in the Alembic migration 003_seed_lookup_data.py
        # So it gets seeded automatically when we run migrations
        print("✅ Initial data seeded successfully (via Alembic migration)")
        return True
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_tenant():
    """Create first tenant and API key."""
    print("👤 Creating first tenant...")
    
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
                name="Default Tenant",
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
                name="Default API Key"
            )
            session.add(api_key)
            session.commit()
            
            print("✅ Tenant created successfully")
            print(f"   Tenant ID: {tenant.id}")
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
    print("🚀 Starting Railway database setup...")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')[:30]}...")
    print()
    
    # Step 1: Run migrations
    if not run_migrations():
        print("❌ Setup failed at migrations step")
        sys.exit(1)
    
    print()
    
    # Step 2: Seed data
    if not seed_data():
        print("❌ Setup failed at seeding step")
        sys.exit(1)
    
    print()
    print("🎉 Railway database setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Test your API endpoints")
    print("2. Create a tenant and API key manually using the API")
    print("3. Start using your API!")
    print()
    print("To create a tenant and API key, use the /v1/admin/tenants endpoint")

if __name__ == "__main__":
    main()
