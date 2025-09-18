"""Tests for API key authentication."""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.auth
class TestAPIAuthentication:
    """Test API key authentication functionality."""
    
    async def test_valid_api_key_success(self, async_test_client: AsyncClient, auth_headers: dict):
        """Test that valid API key allows access."""
        response = await async_test_client.get("/health", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
    
    async def test_missing_api_key_unauthorized(self, async_test_client: AsyncClient):
        """Test that missing API key returns 401."""
        response = await async_test_client.get("/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "API key required" in response.json()["error"]
    
    async def test_invalid_api_key_unauthorized(self, async_test_client: AsyncClient):
        """Test that invalid API key returns 401."""
        headers = {"X-Api-Key": "invalid-key"}
        response = await async_test_client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["error"]
    
    async def test_revoked_api_key_unauthorized(self, async_test_client: AsyncClient, test_db, test_api_key):
        """Test that revoked API key returns 401."""
        # Revoke the API key
        test_api_key.revoked_at = "2024-01-01T00:00:00Z"
        await test_db.commit()
        
        headers = {"X-Api-Key": "test-api-key-123"}
        response = await async_test_client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["error"]
    
    async def test_inactive_tenant_unauthorized(self, async_test_client: AsyncClient, test_db, test_tenant):
        """Test that inactive tenant API key returns 401."""
        # Deactivate the tenant
        test_tenant.is_active = False
        await test_db.commit()
        
        headers = {"X-Api-Key": "test-api-key-123"}
        response = await async_test_client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["error"]
    
    async def test_api_key_case_sensitive(self, async_test_client: AsyncClient):
        """Test that API key is case sensitive."""
        headers = {"X-Api-Key": "TEST-API-KEY-123"}  # Different case
        response = await async_test_client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_api_key_header_name_case_insensitive(self, async_test_client: AsyncClient, auth_headers: dict):
        """Test that header name is case insensitive."""
        headers = {"x-api-key": "test-api-key-123"}  # Lowercase header
        response = await async_test_client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_200_OK
    
    async def test_multiple_api_keys_different_tenants(self, async_test_client: AsyncClient, auth_headers: dict, auth_headers_2: dict):
        """Test that different API keys access different tenant contexts."""
        # Both should work but access different tenant data
        response1 = await async_test_client.get("/health", headers=auth_headers)
        response2 = await async_test_client.get("/health", headers=auth_headers_2)
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
    
    async def test_api_key_with_extra_headers(self, async_test_client: AsyncClient, auth_headers: dict):
        """Test that API key works with additional headers."""
        headers = {
            **auth_headers,
            "Content-Type": "application/json",
            "User-Agent": "Test Client",
            "Accept": "application/json"
        }
        response = await async_test_client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_200_OK
    
    async def test_api_key_whitespace_handling(self, async_test_client: AsyncClient):
        """Test that API key with whitespace is handled correctly."""
        headers = {"X-Api-Key": "  test-api-key-123  "}  # With whitespace
        response = await async_test_client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Should be invalid
    
    async def test_empty_api_key(self, async_test_client: AsyncClient):
        """Test that empty API key returns 401."""
        headers = {"X-Api-Key": ""}
        response = await async_test_client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
