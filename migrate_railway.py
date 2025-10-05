#!/usr/bin/env python3
"""
Simple migration script for Railway.
This script runs the missing migration for api_key_usage table.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def run_migration():
    """Run the specific migration for api_key_usage table."""
    print("🔄 Running migration for api_key_usage table...")
    
    try:
        from alembic.config import Config
        from alembic import command
        from app.core.config import settings
        
        # Set up Alembic configuration
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", str(Path(__file__).parent / "alembic"))
        alembic_cfg.set_main_option("sqlalchemy.url", settings.effective_database_url)
        
        # Run migration to head (this will include the api_key_usage table)
        command.upgrade(alembic_cfg, "head")
        print("✅ Migration completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def check_table_exists():
    """Check if api_key_usage table exists."""
    print("🔍 Checking if api_key_usage table exists...")
    
    try:
        from app.db.session import sync_engine
        from sqlalchemy import text
        
        with sync_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'api_key_usage'
                );
            """))
            exists = result.scalar()
            
            if exists:
                print("✅ api_key_usage table exists")
                return True
            else:
                print("❌ api_key_usage table does not exist")
                return False
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Starting Railway migration for api_key_usage table...")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')[:30]}...")
    print()
    
    # Check if table already exists
    if check_table_exists():
        print("✅ Table already exists, no migration needed")
        return
    
    # Run migration
    if run_migration():
        print("✅ Migration completed successfully")
        
        # Verify table was created
        if check_table_exists():
            print("🎉 api_key_usage table created successfully!")
        else:
            print("❌ Table was not created properly")
    else:
        print("❌ Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
