#!/usr/bin/env python3
"""
Test Railway configuration before deployment.
This script validates that all necessary components are working.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all necessary modules can be imported."""
    print("Testing imports...")
    
    try:
        from app.core.config import settings
        print("✅ Settings imported successfully")
        
        from app.db.session import sync_engine, async_engine
        print("✅ Database engines imported successfully")
        
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_configuration():
    """Test configuration settings."""
    print("\nTesting configuration...")
    
    try:
        from app.core.config import settings
        
        # Test database URL
        db_url = settings.effective_database_url
        print(f"✅ Database URL: {db_url[:20]}...")
        
        # Test port configuration
        port = settings.port
        print(f"✅ Port: {port}")
        
        # Test environment
        env = settings.environment
        print(f"✅ Environment: {env}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_database_connection():
    """Test database connection."""
    print("\nTesting database connection...")
    
    try:
        from app.db.session import sync_engine
        
        # Test connection
        with sync_engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   This is expected if DATABASE_URL is not set or database is not available")
        return False


def test_fastapi_app():
    """Test FastAPI app initialization."""
    print("\nTesting FastAPI app...")
    
    try:
        from app.main import app
        
        # Test that the app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ FastAPI app initialized with {len(routes)} routes")
        
        # Check for health endpoint
        if "/health" in routes:
            print("✅ Health endpoint found")
        else:
            print("⚠️  Health endpoint not found")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Railway configuration...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_database_connection,
        test_fastapi_app,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your configuration is ready for Railway deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
