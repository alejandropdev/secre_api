#!/usr/bin/env python3
"""Test script for auth endpoints."""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx
from app.core.config import settings


async def test_auth_endpoints():
    """Test the authentication endpoints."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing Secre API Authentication Endpoints")
        print("=" * 50)
        
        # Test health check
        print("\n1. Testing health check...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test service info
        print("\n2. Testing service info...")
        try:
            response = await client.get(f"{base_url}/v1/health/info")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test bootstrap (create first tenant and API key)
        print("\n3. Testing bootstrap endpoint...")
        try:
            bootstrap_data = {
                "name": "Test Medical Center"
            }
            response = await client.post(
                f"{base_url}/v1/admin/bootstrap",
                json=bootstrap_data
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                print(f"   Tenant created: {data['api_key']['tenant_id']}")
                print(f"   API Key: {data['plaintext_key'][:8]}...")
                api_key = data['plaintext_key']
            else:
                print(f"   Error: {response.text}")
                api_key = None
        except Exception as e:
            print(f"   Error: {e}")
            api_key = None
        
        if api_key:
            # Test authenticated endpoints
            headers = {"X-Api-Key": api_key}
            
            # Test lookup endpoints
            print("\n4. Testing lookup endpoints...")
            try:
                response = await client.get(f"{base_url}/v1/lookup/document-types", headers=headers)
                print(f"   Document Types Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Found {data['total']} document types")
                
                response = await client.get(f"{base_url}/v1/lookup/genders", headers=headers)
                print(f"   Genders Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Found {data['total']} genders")
            except Exception as e:
                print(f"   Error: {e}")
            
            # Test API key list
            print("\n5. Testing API key list...")
            try:
                response = await client.get(f"{base_url}/v1/auth/api-keys", headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Found {data['total']} API keys")
            except Exception as e:
                print(f"   Error: {e}")
        
        print("\n" + "=" * 50)
        print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_auth_endpoints())
