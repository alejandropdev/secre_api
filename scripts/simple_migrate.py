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
        from sqlalchemy import create_engine
        from app.core.config import settings
        from scripts.init_db import seed_lookup_data
        
        # Create a fresh sync engine for seeding
        engine = create_engine(settings.effective_database_url)
        seed_lookup_data(engine)
        print("✅ Initial data seeded successfully")
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
        from app.core.config import settings
        from scripts.create_tenant_and_apikey import create_tenant_and_apikey
        
        # Create a fresh sync engine for tenant creation
        engine = create_engine(settings.effective_database_url)
        
        # We need to modify the create_tenant_and_apikey function to accept an engine
        # For now, let's create the tenant manually
        from sqlalchemy.orm import sessionmaker
        from app.models.tenant import Tenant
        from app.models.api_key import APIKey
        import secrets
        
        SessionLocal = sessionmaker(bind=engine)
        with SessionLocal() as session:
            # Create tenant
            tenant = Tenant(
                name="Default Tenant",
                is_active=True
            )
            session.add(tenant)
            session.flush()  # Get the tenant ID
            
            # Create API key
            api_key = APIKey(
                tenant_id=tenant.id,
                key=secrets.token_hex(32),
                is_active=True
            )
            session.add(api_key)
            session.commit()
            
            print("✅ Tenant created successfully")
            print(f"   Tenant ID: {tenant.id}")
            print(f"   API Key: {api_key.key}")
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
    
    # Step 3: Create tenant
    if not create_tenant():
        print("❌ Setup failed at tenant creation step")
        sys.exit(1)
    
    print()
    print("🎉 Railway database setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Test your API endpoints")
    print("2. Save your API key securely")
    print("3. Start using your API!")

if __name__ == "__main__":
    main()
