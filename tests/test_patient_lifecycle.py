"""Tests for Patient CRUD lifecycle."""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.api
class TestPatientLifecycle:
    """Test complete patient CRUD lifecycle."""
    
    async def test_create_patient_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test successful patient creation."""
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=sample_patient_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["firstName"] == sample_patient_data["firstName"]
        assert data["firstLastName"] == sample_patient_data["firstLastName"]
        assert data["secondName"] == sample_patient_data["secondName"]
        assert data["secondLastName"] == sample_patient_data["secondLastName"]
        assert data["birthDate"] == sample_patient_data["birthDate"]
        assert data["genderId"] == sample_patient_data["genderId"]
        assert data["documentTypeId"] == sample_patient_data["documentTypeId"]
        assert data["documentNumber"] == sample_patient_data["documentNumber"]
        assert data["phone"] == sample_patient_data["phone"]
        assert data["cellPhone"] == sample_patient_data["cellPhone"]
        assert data["email"] == sample_patient_data["email"]
        assert data["epsId"] == sample_patient_data["epsId"]
        assert data["habeasData"] == sample_patient_data["habeasData"]
        assert data["customFields"] == sample_patient_data["customFields"]
        
        # Verify timestamps
        assert "createdAt" in data
        assert "updatedAt" in data
    
    async def test_get_patient_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test successful patient retrieval."""
        # Create patient first
        create_response = await async_test_client.post(
            "/api/v1/patients/", 
            json=sample_patient_data, 
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        patient_id = create_response.json()["id"]
        
        # Get patient
        response = await async_test_client.get(
            f"/api/v1/patients/{patient_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == patient_id
        assert data["firstName"] == sample_patient_data["firstName"]
    
    async def test_get_patient_not_found(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test patient not found."""
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        response = await async_test_client.get(
            f"/api/v1/patients/{non_existent_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["error"].lower()
    
    async def test_update_patient_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test successful patient update."""
        # Create patient first
        create_response = await async_test_client.post(
            "/api/v1/patients/", 
            json=sample_patient_data, 
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        patient_id = create_response.json()["id"]
        
        # Update patient
        update_data = {
            "firstName": "Updated Name",
            "email": "updated@example.com",
            "customFields": {
                "emergencyContact": "Updated Contact",
                "newField": "new value"
            }
        }
        
        response = await async_test_client.patch(
            f"/api/v1/patients/{patient_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["firstName"] == update_data["firstName"]
        assert data["email"] == update_data["email"]
        assert data["customFields"]["emergencyContact"] == update_data["customFields"]["emergencyContact"]
        assert data["customFields"]["newField"] == update_data["customFields"]["newField"]
        
        # Verify other fields unchanged
        assert data["firstLastName"] == sample_patient_data["firstLastName"]
        assert data["documentNumber"] == sample_patient_data["documentNumber"]
    
    async def test_update_patient_not_found(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test update patient not found."""
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        update_data = {"firstName": "Updated Name"}
        response = await async_test_client.patch(
            f"/api/v1/patients/{non_existent_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["error"].lower()
    
    async def test_delete_patient_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test successful patient deletion."""
        # Create patient first
        create_response = await async_test_client.post(
            "/api/v1/patients/", 
            json=sample_patient_data, 
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        patient_id = create_response.json()["id"]
        
        # Delete patient
        response = await async_test_client.delete(
            f"/api/v1/patients/{patient_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Patient deleted successfully"
        
        # Verify patient is deleted
        get_response = await async_test_client.get(
            f"/api/v1/patients/{patient_id}", 
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_delete_patient_not_found(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test delete patient not found."""
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        response = await async_test_client.delete(
            f"/api/v1/patients/{non_existent_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["error"].lower()
    
    async def test_search_patients_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test successful patient search."""
        # Create multiple patients
        patient_data_1 = sample_patient_data.copy()
        patient_data_1["documentNumber"] = "11111111"
        patient_data_1["email"] = "patient1@example.com"
        
        patient_data_2 = sample_patient_data.copy()
        patient_data_2["documentNumber"] = "22222222"
        patient_data_2["email"] = "patient2@example.com"
        
        # Create patients
        await async_test_client.post("/api/v1/patients/", json=patient_data_1, headers=auth_headers)
        await async_test_client.post("/api/v1/patients/", json=patient_data_2, headers=auth_headers)
        
        # Search by email
        response = await async_test_client.get(
            "/api/v1/patients/?email=patient1@example.com", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["email"] == "patient1@example.com"
    
    async def test_search_patients_pagination(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test patient search pagination."""
        # Create multiple patients
        for i in range(5):
            patient_data = sample_patient_data.copy()
            patient_data["documentNumber"] = f"1111111{i}"
            patient_data["email"] = f"patient{i}@example.com"
            await async_test_client.post("/api/v1/patients/", json=patient_data, headers=auth_headers)
        
        # Test pagination
        response = await async_test_client.get(
            "/api/v1/patients/?page=1&size=2", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total"] == 5
    
    async def test_duplicate_document_number_validation(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test that duplicate document numbers are rejected."""
        # Create first patient
        response1 = await async_test_client.post(
            "/api/v1/patients/", 
            json=sample_patient_data, 
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create second patient with same document
        response2 = await async_test_client.post(
            "/api/v1/patients/", 
            json=sample_patient_data, 
            headers=auth_headers
        )
        
        assert response2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "already exists" in response2.json()["error"].lower()
        assert response2.json()["field"] == "document_number"
