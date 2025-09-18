"""Tests for Appointment CRUD lifecycle."""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.api
class TestAppointmentLifecycle:
    """Test complete appointment CRUD lifecycle."""
    
    async def test_create_appointment_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test successful appointment creation."""
        response = await async_test_client.post(
            "/api/v1/appointments/", 
            json=sample_appointment_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["startAppointment"] == sample_appointment_data["startAppointment"]
        assert data["endAppointment"] == sample_appointment_data["endAppointment"]
        assert data["patientDocumentTypeId"] == sample_appointment_data["patientDocumentTypeId"]
        assert data["patientDocumentNumber"] == sample_appointment_data["patientDocumentNumber"]
        assert data["doctorDocumentTypeId"] == sample_appointment_data["doctorDocumentTypeId"]
        assert data["doctorDocumentNumber"] == sample_appointment_data["doctorDocumentNumber"]
        assert data["modality"] == sample_appointment_data["modality"]
        assert data["state"] == sample_appointment_data["state"]
        assert data["notificationState"] == sample_appointment_data["notificationState"]
        assert data["appointmentType"] == sample_appointment_data["appointmentType"]
        assert data["clinicId"] == sample_appointment_data["clinicId"]
        assert data["comment"] == sample_appointment_data["comment"]
        assert data["customFields"] == sample_appointment_data["customFields"]
        
        # Verify timestamps
        assert "createdAt" in data
        assert "updatedAt" in data
    
    async def test_get_appointment_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test successful appointment retrieval."""
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
        assert data["id"] == appointment_id
        assert data["patientDocumentNumber"] == sample_appointment_data["patientDocumentNumber"]
    
    async def test_get_appointment_not_found(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test appointment not found."""
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        response = await async_test_client.get(
            f"/api/v1/appointments/{non_existent_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["error"].lower()
    
    async def test_update_appointment_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test successful appointment update."""
        # Create appointment first
        create_response = await async_test_client.post(
            "/api/v1/appointments/", 
            json=sample_appointment_data, 
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        appointment_id = create_response.json()["id"]
        
        # Update appointment
        update_data = {
            "state": "confirmed",
            "notificationState": "sent",
            "comment": "Updated comment",
            "customFields": {
                "room": "B202",
                "specialInstructions": "Updated instructions"
            }
        }
        
        response = await async_test_client.patch(
            f"/api/v1/appointments/{appointment_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["state"] == update_data["state"]
        assert data["notificationState"] == update_data["notificationState"]
        assert data["comment"] == update_data["comment"]
        assert data["customFields"]["room"] == update_data["customFields"]["room"]
        assert data["customFields"]["specialInstructions"] == update_data["customFields"]["specialInstructions"]
        
        # Verify other fields unchanged
        assert data["patientDocumentNumber"] == sample_appointment_data["patientDocumentNumber"]
        assert data["modality"] == sample_appointment_data["modality"]
    
    async def test_update_appointment_not_found(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test update appointment not found."""
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        update_data = {"state": "confirmed"}
        response = await async_test_client.patch(
            f"/api/v1/appointments/{non_existent_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["error"].lower()
    
    async def test_delete_appointment_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test successful appointment deletion."""
        # Create appointment first
        create_response = await async_test_client.post(
            "/api/v1/appointments/", 
            json=sample_appointment_data, 
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        appointment_id = create_response.json()["id"]
        
        # Delete appointment
        response = await async_test_client.delete(
            f"/api/v1/appointments/{appointment_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Appointment deleted successfully"
        
        # Verify appointment is deleted
        get_response = await async_test_client.get(
            f"/api/v1/appointments/{appointment_id}", 
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_delete_appointment_not_found(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test delete appointment not found."""
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        response = await async_test_client.delete(
            f"/api/v1/appointments/{non_existent_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["error"].lower()
    
    async def test_search_appointments_success(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test successful appointment search."""
        # Create multiple appointments
        appointment_data_1 = sample_appointment_data.copy()
        appointment_data_1["patientDocumentNumber"] = "11111111"
        appointment_data_1["state"] = "scheduled"
        
        appointment_data_2 = sample_appointment_data.copy()
        appointment_data_2["patientDocumentNumber"] = "22222222"
        appointment_data_2["state"] = "confirmed"
        
        # Create appointments
        await async_test_client.post("/api/v1/appointments/", json=appointment_data_1, headers=auth_headers)
        await async_test_client.post("/api/v1/appointments/", json=appointment_data_2, headers=auth_headers)
        
        # Search by state
        response = await async_test_client.get(
            "/api/v1/appointments/?state=scheduled", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["state"] == "scheduled"
    
    async def test_search_appointments_by_date_range(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test appointment search by date range."""
        # Create appointments with different dates
        appointment_data_1 = sample_appointment_data.copy()
        appointment_data_1["startAppointment"] = "2024-01-15T10:00:00-05:00"
        appointment_data_1["endAppointment"] = "2024-01-15T11:00:00-05:00"
        
        appointment_data_2 = sample_appointment_data.copy()
        appointment_data_2["startAppointment"] = "2024-01-20T10:00:00-05:00"
        appointment_data_2["endAppointment"] = "2024-01-20T11:00:00-05:00"
        
        # Create appointments
        await async_test_client.post("/api/v1/appointments/", json=appointment_data_1, headers=auth_headers)
        await async_test_client.post("/api/v1/appointments/", json=appointment_data_2, headers=auth_headers)
        
        # Search by date range
        response = await async_test_client.get(
            "/api/v1/appointments/?startDate=2024-01-15&endDate=2024-01-16", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert "2024-01-15" in data["items"][0]["startAppointment"]
    
    async def test_search_appointments_pagination(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test appointment search pagination."""
        # Create multiple appointments
        for i in range(5):
            appointment_data = sample_appointment_data.copy()
            appointment_data["patientDocumentNumber"] = f"1111111{i}"
            appointment_data["startAppointment"] = f"2024-01-1{i}T10:00:00-05:00"
            appointment_data["endAppointment"] = f"2024-01-1{i}T11:00:00-05:00"
            await async_test_client.post("/api/v1/appointments/", json=appointment_data, headers=auth_headers)
        
        # Test pagination
        response = await async_test_client.get(
            "/api/v1/appointments/?page=1&size=2", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total"] == 5
