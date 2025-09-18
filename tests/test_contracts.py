"""Contract tests using OpenAPI examples."""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.unit
class TestAPIContracts:
    """Test API contracts match OpenAPI specification."""
    
    async def test_patient_create_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test patient creation matches OpenAPI contract."""
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=sample_patient_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify response matches expected schema
        data = response.json()
        required_fields = [
            "id", "firstName", "firstLastName", "secondName", "secondLastName",
            "birthDate", "genderId", "documentTypeId", "documentNumber",
            "phone", "cellPhone", "email", "epsId", "habeasData", "customFields",
            "createdAt", "updatedAt"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(data["id"], str)
        assert isinstance(data["firstName"], str)
        assert isinstance(data["firstLastName"], str)
        assert isinstance(data["birthDate"], str)
        assert isinstance(data["genderId"], int)
        assert isinstance(data["documentTypeId"], int)
        assert isinstance(data["documentNumber"], str)
        assert isinstance(data["habeasData"], bool)
        assert isinstance(data["customFields"], dict)
        assert isinstance(data["createdAt"], str)
        assert isinstance(data["updatedAt"], str)
    
    async def test_patient_get_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test patient retrieval matches OpenAPI contract."""
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
        
        # Verify response structure matches GET contract
        required_fields = [
            "id", "firstName", "firstLastName", "secondName", "secondLastName",
            "birthDate", "genderId", "documentTypeId", "documentNumber",
            "phone", "cellPhone", "email", "epsId", "habeasData", "customFields",
            "createdAt", "updatedAt"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    async def test_patient_list_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test patient list matches OpenAPI contract."""
        # Create some patients
        for i in range(3):
            patient_data = sample_patient_data.copy()
            patient_data["documentNumber"] = f"1234567{i}"
            patient_data["email"] = f"patient{i}@example.com"
            
            await async_test_client.post(
                "/api/v1/patients/", 
                json=patient_data, 
                headers=auth_headers
            )
        
        # Get patient list
        response = await async_test_client.get(
            "/api/v1/patients/", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        
        # Verify items structure
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 3
        
        for item in data["items"]:
            assert "id" in item
            assert "firstName" in item
            assert "firstLastName" in item
    
    async def test_appointment_create_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test appointment creation matches OpenAPI contract."""
        response = await async_test_client.post(
            "/api/v1/appointments/", 
            json=sample_appointment_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify response matches expected schema
        data = response.json()
        required_fields = [
            "id", "startAppointment", "endAppointment", "patientDocumentTypeId",
            "patientDocumentNumber", "doctorDocumentTypeId", "doctorDocumentNumber",
            "modality", "state", "notificationState", "appointmentType", "clinicId",
            "comment", "customFields", "createdAt", "updatedAt"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(data["id"], str)
        assert isinstance(data["startAppointment"], str)
        assert isinstance(data["endAppointment"], str)
        assert isinstance(data["patientDocumentTypeId"], int)
        assert isinstance(data["patientDocumentNumber"], str)
        assert isinstance(data["doctorDocumentTypeId"], int)
        assert isinstance(data["doctorDocumentNumber"], str)
        assert isinstance(data["modality"], str)
        assert isinstance(data["state"], str)
        assert isinstance(data["customFields"], dict)
        assert isinstance(data["createdAt"], str)
        assert isinstance(data["updatedAt"], str)
    
    async def test_appointment_get_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test appointment retrieval matches OpenAPI contract."""
        # Create appointment first
        create_response = await async_test_client.post(
            "/api/v1/appointments/", 
            json=sample_appointment_data, 
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        appointment_id = create_response.json()["id"]
        
        # Get appointment
        response = await async_test_client.get(
            f"/api/v1/appointments/{appointment_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify response structure matches GET contract
        required_fields = [
            "id", "startAppointment", "endAppointment", "patientDocumentTypeId",
            "patientDocumentNumber", "doctorDocumentTypeId", "doctorDocumentNumber",
            "modality", "state", "notificationState", "appointmentType", "clinicId",
            "comment", "customFields", "createdAt", "updatedAt"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    async def test_appointment_list_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test appointment list matches OpenAPI contract."""
        # Create some appointments
        for i in range(3):
            appointment_data = sample_appointment_data.copy()
            appointment_data["patientDocumentNumber"] = f"1234567{i}"
            appointment_data["startAppointment"] = f"2024-01-1{i}T10:00:00-05:00"
            appointment_data["endAppointment"] = f"2024-01-1{i}T11:00:00-05:00"
            
            await async_test_client.post(
                "/api/v1/appointments/", 
                json=appointment_data, 
                headers=auth_headers
            )
        
        # Get appointment list
        response = await async_test_client.get(
            "/api/v1/appointments/", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        
        # Verify items structure
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 3
        
        for item in data["items"]:
            assert "id" in item
            assert "startAppointment" in item
            assert "endAppointment" in item
            assert "patientDocumentNumber" in item
    
    async def test_error_response_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test error responses match OpenAPI contract."""
        # Test 404 error
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        response = await async_test_client.get(
            f"/api/v1/patients/{non_existent_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        # Verify error response structure
        assert "error" in data
        assert "trace_id" in data
        assert "timestamp" in data
        
        # Verify field types
        assert isinstance(data["error"], str)
        assert isinstance(data["trace_id"], str)
        assert isinstance(data["timestamp"], str)
    
    async def test_validation_error_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test validation error responses match OpenAPI contract."""
        # Test with invalid data
        invalid_data = {
            "eventType": "PATIENT",
            "actionType": "CREATE",
            "firstName": "",  # Invalid empty name
            "documentNumber": "",  # Invalid empty document
        }
        
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=invalid_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        
        # Verify validation error response structure
        assert "error" in data
        assert "trace_id" in data
        assert "timestamp" in data
        assert "field" in data  # Should include field information
        
        # Verify field types
        assert isinstance(data["error"], str)
        assert isinstance(data["trace_id"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["field"], str)
    
    async def test_health_check_contract(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test health check endpoint matches contract."""
        response = await async_test_client.get(
            "/health", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify health check response structure
        assert "status" in data
        assert "version" in data
        
        # Verify field types and values
        assert data["status"] == "healthy"
        assert isinstance(data["version"], str)
    
    async def test_root_endpoint_contract(
        self, 
        async_test_client: AsyncClient
    ):
        """Test root endpoint matches contract."""
        response = await async_test_client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify root endpoint response structure
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        
        # Verify field types
        assert isinstance(data["message"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["docs"], str)
        assert data["docs"] == "/docs"
