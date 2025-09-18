"""Tests for Row-Level Security (RLS) functionality."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import set_tenant_context
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.tenant import Tenant
from app.models.api_key import ApiKey


@pytest.mark.asyncio
@pytest.mark.rls
class TestRLSTenantIsolation:
    """Test Row-Level Security tenant isolation."""
    
    async def test_tenant_a_cannot_see_tenant_b_patients(
        self, 
        async_test_client: AsyncClient, 
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_tenant_2: Tenant,
        auth_headers: dict,
        auth_headers_2: dict,
        sample_patient_data: dict
    ):
        """Test that tenant A cannot see tenant B's patients."""
        
        # Create patient for tenant 1
        patient_data_1 = sample_patient_data.copy()
        patient_data_1["documentNumber"] = "11111111"
        
        response1 = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data_1, 
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_201_CREATED
        patient1_id = response1.json()["id"]
        
        # Create patient for tenant 2
        patient_data_2 = sample_patient_data.copy()
        patient_data_2["documentNumber"] = "22222222"
        
        response2 = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data_2, 
            headers=auth_headers_2
        )
        assert response2.status_code == status.HTTP_201_CREATED
        patient2_id = response2.json()["id"]
        
        # Tenant 1 should only see their own patient
        response = await async_test_client.get(
            f"/api/v1/patients/{patient1_id}", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Tenant 1 should not see tenant 2's patient
        response = await async_test_client.get(
            f"/api/v1/patients/{patient2_id}", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Tenant 2 should only see their own patient
        response = await async_test_client.get(
            f"/api/v1/patients/{patient2_id}", 
            headers=auth_headers_2
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Tenant 2 should not see tenant 1's patient
        response = await async_test_client.get(
            f"/api/v1/patients/{patient1_id}", 
            headers=auth_headers_2
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_tenant_a_cannot_update_tenant_b_patients(
        self, 
        async_test_client: AsyncClient, 
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_tenant_2: Tenant,
        auth_headers: dict,
        auth_headers_2: dict,
        sample_patient_data: dict
    ):
        """Test that tenant A cannot update tenant B's patients."""
        
        # Create patient for tenant 2
        patient_data_2 = sample_patient_data.copy()
        patient_data_2["documentNumber"] = "22222222"
        
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data_2, 
            headers=auth_headers_2
        )
        assert response.status_code == status.HTTP_201_CREATED
        patient2_id = response.json()["id"]
        
        # Tenant 1 should not be able to update tenant 2's patient
        update_data = {"firstName": "Hacked Name"}
        response = await async_test_client.patch(
            f"/api/v1/patients/{patient2_id}", 
            json=update_data, 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_tenant_a_cannot_delete_tenant_b_patients(
        self, 
        async_test_client: AsyncClient, 
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_tenant_2: Tenant,
        auth_headers: dict,
        auth_headers_2: dict,
        sample_patient_data: dict
    ):
        """Test that tenant A cannot delete tenant B's patients."""
        
        # Create patient for tenant 2
        patient_data_2 = sample_patient_data.copy()
        patient_data_2["documentNumber"] = "22222222"
        
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data_2, 
            headers=auth_headers_2
        )
        assert response.status_code == status.HTTP_201_CREATED
        patient2_id = response.json()["id"]
        
        # Tenant 1 should not be able to delete tenant 2's patient
        response = await async_test_client.delete(
            f"/api/v1/patients/{patient2_id}", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_tenant_a_cannot_see_tenant_b_appointments(
        self, 
        async_test_client: AsyncClient, 
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_tenant_2: Tenant,
        auth_headers: dict,
        auth_headers_2: dict,
        sample_appointment_data: dict
    ):
        """Test that tenant A cannot see tenant B's appointments."""
        
        # Create appointment for tenant 1
        appointment_data_1 = sample_appointment_data.copy()
        appointment_data_1["patientDocumentNumber"] = "11111111"
        
        response1 = await async_test_client.post(
            "/api/v1/appointments/", 
            json=appointment_data_1, 
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_201_CREATED
        appointment1_id = response1.json()["id"]
        
        # Create appointment for tenant 2
        appointment_data_2 = sample_appointment_data.copy()
        appointment_data_2["patientDocumentNumber"] = "22222222"
        
        response2 = await async_test_client.post(
            "/api/v1/appointments/", 
            json=appointment_data_2, 
            headers=auth_headers_2
        )
        assert response2.status_code == status.HTTP_201_CREATED
        appointment2_id = response2.json()["id"]
        
        # Tenant 1 should only see their own appointment
        response = await async_test_client.get(
            f"/api/v1/appointments/{appointment1_id}", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Tenant 1 should not see tenant 2's appointment
        response = await async_test_client.get(
            f"/api/v1/appointments/{appointment2_id}", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_tenant_search_isolation(
        self, 
        async_test_client: AsyncClient, 
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_tenant_2: Tenant,
        auth_headers: dict,
        auth_headers_2: dict,
        sample_patient_data: dict
    ):
        """Test that tenant search only returns their own data."""
        
        # Create patients for both tenants
        patient_data_1 = sample_patient_data.copy()
        patient_data_1["documentNumber"] = "11111111"
        patient_data_1["email"] = "tenant1@example.com"
        
        patient_data_2 = sample_patient_data.copy()
        patient_data_2["documentNumber"] = "22222222"
        patient_data_2["email"] = "tenant2@example.com"
        
        # Create patient for tenant 1
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data_1, 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Create patient for tenant 2
        response = await async_test_client.post(
            "/api/v1/patients/", 
            json=patient_data_2, 
            headers=auth_headers_2
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Tenant 1 search should only return their patient
        response = await async_test_client.get(
            "/api/v1/patients/?email=tenant1@example.com", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        patients = response.json()["items"]
        assert len(patients) == 1
        assert patients[0]["email"] == "tenant1@example.com"
        
        # Tenant 1 search should not find tenant 2's patient
        response = await async_test_client.get(
            "/api/v1/patients/?email=tenant2@example.com", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        patients = response.json()["items"]
        assert len(patients) == 0
    
    async def test_database_rls_policy_enforcement(
        self, 
        test_db: AsyncSession,
        test_tenant: Tenant,
        test_tenant_2: Tenant
    ):
        """Test that RLS policies are enforced at database level."""
        
        # Set tenant context for tenant 1
        set_tenant_context(str(test_tenant.id))
        
        # Create a patient for tenant 1
        patient1 = Patient(
            tenant_id=test_tenant.id,
            first_name="Patient 1",
            first_last_name="Last Name",
            birth_date="1990-01-01",
            gender_id=1,
            document_type_id=1,
            document_number="11111111"
        )
        test_db.add(patient1)
        await test_db.commit()
        await test_db.refresh(patient1)
        
        # Set tenant context for tenant 2
        set_tenant_context(str(test_tenant_2.id))
        
        # Try to query patient 1 from tenant 2 context - should not find it
        from sqlalchemy import select
        result = await test_db.execute(
            select(Patient).where(Patient.id == patient1.id)
        )
        patient = result.scalar_one_or_none()
        assert patient is None  # RLS should prevent access
        
        # Switch back to tenant 1 context
        set_tenant_context(str(test_tenant.id))
        
        # Now should be able to find the patient
        result = await test_db.execute(
            select(Patient).where(Patient.id == patient1.id)
        )
        patient = result.scalar_one_or_none()
        assert patient is not None
        assert patient.first_name == "Patient 1"
