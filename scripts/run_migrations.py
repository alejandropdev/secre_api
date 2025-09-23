#!/usr/bin/env python3
"""
Simple migration script for Railway deployment.
Run this in the Railway environment.
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
        
        # Set up Alembic configuration
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", str(Path(__file__).parent.parent / "alembic"))
        # Use the sync database URL for migrations
        alembic_cfg.set_main_option("sqlalchemy.url", settings.effective_database_url)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def seed_data():
    """Seed initial lookup data."""
    print("🌱 Seeding initial data...")
    
    try:
        from app.db.session import sync_engine
        from scripts.init_db import seed_lookup_data
        
        seed_lookup_data(sync_engine)
        print("✅ Initial data seeded successfully")
        return True
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return False

def create_tenant():
    """Create first tenant and API key."""
    print("👤 Creating first tenant...")
    
    try:
        from scripts.create_tenant_and_apikey import create_tenant_and_apikey
        
        tenant_id, api_key = create_tenant_and_apikey("Default Tenant")
        print("✅ Tenant created successfully")
        print(f"   Tenant ID: {tenant_id}")
        print(f"   API Key: {api_key}")
        print("   🔐 Keep this API key safe - you'll need it to access the API!")
        return True
    except Exception as e:
        print(f"❌ Tenant creation failed: {e}")
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
