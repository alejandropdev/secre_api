"""Tests for validation and normalization functionality."""

import pytest
from datetime import datetime, timezone
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.unit
class TestDateValidationAndUTCConversion:
    """Test date parsing and UTC conversion."""
    
    async def test_valid_rfc3339_date_parsing(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test that valid RFC3339 dates are parsed correctly."""
        # Test various timezone formats
        test_cases = [
            "2024-01-15T10:00:00-05:00",  # EST
            "2024-01-15T10:00:00+00:00",  # UTC
            "2024-01-15T10:00:00+02:00",  # CET
            "2024-01-15T10:00:00Z",       # UTC with Z
        ]
        
        for start_time in test_cases:
            appointment_data = sample_appointment_data.copy()
            appointment_data["startAppointment"] = start_time
            appointment_data["endAppointment"] = "2024-01-15T11:00:00-05:00"
            
            response = await async_test_client.post(
                "/api/v1/appointments/", 
                json=appointment_data, 
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            # Verify the date was stored in UTC
            assert "T" in data["startAppointment"]
            assert data["startAppointment"].endswith("Z") or "+00:00" in data["startAppointment"]
    
    async def test_invalid_date_format_rejection(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test that invalid date formats are rejected."""
        invalid_dates = [
            "2024-01-15 10:00:00",  # Missing T
            "15/01/2024 10:00",     # Wrong format
            "2024-13-15T10:00:00",  # Invalid month
            "2024-01-32T10:00:00",  # Invalid day
            "2024-01-15T25:00:00",  # Invalid hour
            "not-a-date",           # Not a date
        ]
        
        for invalid_date in invalid_dates:
            appointment_data = sample_appointment_data.copy()
            appointment_data["startAppointment"] = invalid_date
            appointment_data["endAppointment"] = "2024-01-15T11:00:00-05:00"
            
            response = await async_test_client.post(
                "/api/v1/appointments/", 
                json=appointment_data, 
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "validation error" in response.json()["error"].lower()
    
    async def test_end_time_before_start_time_rejection(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test that end time before start time is rejected."""
        appointment_data = sample_appointment_data.copy()
        appointment_data["startAppointment"] = "2024-01-15T11:00:00-05:00"
        appointment_data["endAppointment"] = "2024-01-15T10:00:00-05:00"  # End before start
        
        response = await async_test_client.post(
            "/api/v1/appointments/", 
            json=appointment_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "end time must be after start time" in response.json()["error"].lower()
        assert response.json()["field"] == "endAppointment"
    
    async def test_utc_conversion_accuracy(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test that UTC conversion is accurate."""
        # Test EST to UTC conversion
        appointment_data = sample_appointment_data.copy()
        appointment_data["startAppointment"] = "2024-01-15T10:00:00-05:00"  # EST
        appointment_data["endAppointment"] = "2024-01-15T11:00:00-05:00"    # EST
        
        response = await async_test_client.post(
            "/api/v1/appointments/", 
            json=appointment_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # EST is UTC-5, so 10:00 EST = 15:00 UTC
        assert "15:00:00" in data["startAppointment"]
        assert "16:00:00" in data["endAppointment"]
    
    async def test_timezone_awareness(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test that timezone information is preserved."""
        appointment_data = sample_appointment_data.copy()
        appointment_data["startAppointment"] = "2024-01-15T10:00:00-05:00"
        appointment_data["endAppointment"] = "2024-01-15T11:00:00-05:00"
        
        response = await async_test_client.post(
            "/api/v1/appointments/", 
            json=appointment_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify UTC format
        start_utc = datetime.fromisoformat(data["startAppointment"].replace("Z", "+00:00"))
        end_utc = datetime.fromisoformat(data["endAppointment"].replace("Z", "+00:00"))
        
        assert start_utc.tzinfo == timezone.utc
        assert end_utc.tzinfo == timezone.utc
        assert end_utc > start_utc


@pytest.mark.asyncio
@pytest.mark.unit
class TestDocumentValidation:
    """Test document type and number validation."""
    
    async def test_valid_document_types(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test that valid document types are accepted."""
        valid_document_types = [1, 2, 3, 4, 5]  # Assuming these are valid
        
        for doc_type in valid_document_types:
            patient_data = sample_patient_data.copy()
            patient_data["documentTypeId"] = doc_type
            patient_data["documentNumber"] = f"1234567{doc_type}"
            
            response = await async_test_client.post(
                "/api/v1/patients/", 
                json=patient_data, 
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
    
    async def test_invalid_document_type_rejection(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test that invalid document types are rejected."""
        invalid_document_types = [0, -1, 999, "invalid"]
        
        for doc_type in invalid_document_types:
            patient_data = sample_patient_data.copy()
            patient_data["documentTypeId"] = doc_type
            patient_data["documentNumber"] = "12345678"
            
            response = await async_test_client.post(
                "/api/v1/patients/", 
                json=patient_data, 
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_document_number_validation(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test document number validation."""
        # Test empty document number
        patient_data = sample_patient_data.copy()
        patient_data["documentNumber"] = ""
        
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "document number" in response.json()["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
class TestModalityValidation:
    """Test appointment modality validation."""
    
    async def test_valid_modalities(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test that valid modalities are accepted."""
        valid_modalities = ["presencial", "virtual", "telemedicina", "domicilio"]
        
        for modality in valid_modalities:
            appointment_data = sample_appointment_data.copy()
            appointment_data["modality"] = modality
            appointment_data["patientDocumentNumber"] = f"1234567{hash(modality) % 1000}"
            
            response = await async_test_client.post(
                "/api/v1/appointments/", 
                json=appointment_data, 
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
    
    async def test_invalid_modality_rejection(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_appointment_data: dict
    ):
        """Test that invalid modalities are rejected."""
        invalid_modalities = ["invalid", "online", "offline", ""]
        
        for modality in invalid_modalities:
            appointment_data = sample_appointment_data.copy()
            appointment_data["modality"] = modality
            appointment_data["patientDocumentNumber"] = f"1234567{hash(modality) % 1000}"
            
            response = await async_test_client.post(
                "/api/v1/appointments/", 
                json=appointment_data, 
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.unit
class TestCustomFieldsValidation:
    """Test custom fields validation and round-trip."""
    
    async def test_custom_fields_round_trip(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test that custom fields are preserved through create/read cycle."""
        custom_fields = {
            "emergencyContact": "María González",
            "emergencyPhone": "+57-300-987-6543",
            "allergies": ["penicilina", "aspirina"],
            "medicalHistory": {
                "diabetes": True,
                "hypertension": False,
                "lastCheckup": "2023-12-01"
            },
            "preferences": {
                "language": "es",
                "notifications": True
            }
        }
        
        patient_data = sample_patient_data.copy()
        patient_data["customFields"] = custom_fields
        
        # Create patient
        create_response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data, 
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        patient_id = create_response.json()["id"]
        
        # Read patient
        get_response = await async_test_client.get(
            f"/api/v1/patients/{patient_id}", 
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        # Verify custom fields are preserved
        retrieved_custom_fields = get_response.json()["customFields"]
        assert retrieved_custom_fields == custom_fields
        assert retrieved_custom_fields["emergencyContact"] == "María González"
        assert retrieved_custom_fields["allergies"] == ["penicilina", "aspirina"]
        assert retrieved_custom_fields["medicalHistory"]["diabetes"] is True
        assert retrieved_custom_fields["preferences"]["language"] == "es"
    
    async def test_custom_fields_update(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test that custom fields can be updated."""
        # Create patient with initial custom fields
        patient_data = sample_patient_data.copy()
        patient_data["customFields"] = {"initialField": "initialValue"}
        
        create_response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data, 
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        patient_id = create_response.json()["id"]
        
        # Update custom fields
        update_data = {
            "customFields": {
                "initialField": "updatedValue",
                "newField": "newValue",
                "nestedField": {
                    "level1": {
                        "level2": "deepValue"
                    }
                }
            }
        }
        
        update_response = await async_test_client.patch(
            f"/api/v1/patients/{patient_id}", 
            json=update_data, 
            headers=auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # Verify updated custom fields
        get_response = await async_test_client.get(
            f"/api/v1/patients/{patient_id}", 
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        retrieved_custom_fields = get_response.json()["customFields"]
        assert retrieved_custom_fields["initialField"] == "updatedValue"
        assert retrieved_custom_fields["newField"] == "newValue"
        assert retrieved_custom_fields["nestedField"]["level1"]["level2"] == "deepValue"
    
    async def test_empty_custom_fields(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test that empty custom fields are handled correctly."""
        patient_data = sample_patient_data.copy()
        patient_data["customFields"] = {}
        
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["customFields"] == {}
    
    async def test_custom_fields_with_null_values(
        self, 
        async_test_client: AsyncClient, 
        auth_headers: dict,
        sample_patient_data: dict
    ):
        """Test that custom fields with null values are handled correctly."""
        custom_fields = {
            "stringField": "value",
            "nullField": None,
            "numberField": 42,
            "booleanField": True
        }
        
        patient_data = sample_patient_data.copy()
        patient_data["customFields"] = custom_fields
        
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["customFields"]["stringField"] == "value"
        assert data["customFields"]["nullField"] is None
        assert data["customFields"]["numberField"] == 42
        assert data["customFields"]["booleanField"] is True
