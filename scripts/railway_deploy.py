#!/usr/bin/env python3
"""
Railway deployment helper script.
This script helps set up the database and create initial data after Railway deployment.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import psycopg2
        import sqlalchemy
        import alembic
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("This script should be run in the Railway environment where dependencies are installed.")
        return False

# Check dependencies first
if not check_dependencies():
    print("\n💡 To run this script:")
    print("1. Use Railway CLI: railway run python scripts/railway_deploy.py")
    print("2. Or use Railway dashboard shell")
    print("3. Or run manually in Railway environment")
    sys.exit(1)

from app.core.config import settings
from app.db.session import sync_engine
from alembic.config import Config
from alembic import command


def run_migrations():
    """Run database migrations."""
    print("Running database migrations...")
    
    # Set up Alembic configuration
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(Path(__file__).parent.parent / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.effective_database_url)
    
    try:
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def seed_initial_data():
    """Seed initial lookup data."""
    print("Seeding initial data...")
    
    try:
        from scripts.init_db import seed_lookup_data
        seed_lookup_data(sync_engine)
        print("✅ Initial data seeded successfully")
        return True
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return False


def create_tenant_and_api_key(tenant_name: str = "Default Tenant"):
    """Create a tenant and API key."""
    print(f"Creating tenant: {tenant_name}")
    
    try:
        from scripts.create_tenant_and_apikey import create_tenant_and_apikey
        tenant_id, api_key = create_tenant_and_apikey(tenant_name)
        print(f"✅ Tenant created successfully")
        print(f"   Tenant ID: {tenant_id}")
        print(f"   API Key: {api_key}")
        print(f"   Keep this API key safe - you'll need it to access the API!")
        return True
    except Exception as e:
        print(f"❌ Tenant creation failed: {e}")
        return False


def main():
    """Main deployment function."""
    print("🚀 Starting Railway deployment setup...")
    print(f"Database URL: {settings.effective_database_url}")
    print(f"Environment: {settings.environment}")
    print()
    
    # Step 1: Run migrations
    if not run_migrations():
        print("❌ Deployment setup failed at migrations step")
        sys.exit(1)
    
    print()
    
    # Step 2: Seed initial data
    if not seed_initial_data():
        print("❌ Deployment setup failed at seeding step")
        sys.exit(1)
    
    print()
    
    # Step 3: Create tenant and API key
    tenant_name = os.getenv("TENANT_NAME", "Default Tenant")
    if not create_tenant_and_api_key(tenant_name):
        print("❌ Deployment setup failed at tenant creation step")
        sys.exit(1)
    
    print()
    print("🎉 Railway deployment setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Test your API endpoints")
    print("2. Update your environment variables in Railway dashboard")
    print("3. Set up monitoring and alerting")
    print("4. Configure custom domain if needed")


if __name__ == "__main__":
    main()
