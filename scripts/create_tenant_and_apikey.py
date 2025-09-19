#!/usr/bin/env python3
"""Script to create demo tenant and API key."""

import asyncio
import sys
from datetime import date, datetime
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.api_key_service import ApiKeyService
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService
from app.services.tenant_service import TenantService


async def create_demo_data():
    """Create demo tenant and API key."""
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
    )
    
    # Create session factory
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with AsyncSessionLocal() as db:
        # Create tenant service
        tenant_service = TenantService(db)
        
        # Create demo tenant
        print("Creating demo tenant...")
        tenant = await tenant_service.create_tenant("Demo Medical Center")
        print(f"Created tenant: {tenant.name} (ID: {tenant.id})")
        
        # Create API key service
        api_key_service = ApiKeyService(db)
        
        # Create demo API key
        print("Creating demo API key...")
        plaintext_key, api_key = await api_key_service.create_api_key(
            tenant_id=tenant.id,
            name="Demo API Key"
        )
        
        print(f"Created API key: {api_key.name} (ID: {api_key.id})")
        print(f"API Key (save this securely): {plaintext_key}")
        print(f"API Key Hash: {api_key.key_hash}")
        
        # Create sample patient
        print("\nCreating sample patient...")
        patient_service = PatientService(db)
        patient = await patient_service.create_patient(
            tenant_id=tenant.id,
            first_name="Juan",
            first_last_name="Pérez",
            birth_date=date(1985, 5, 15),
            gender_id=1,  # Male
            document_type_id=1,  # CC
            document_number="12345678",
            email="juan.perez@example.com",
            phone="+57-1-234-5678",
            cell_phone="+57-300-123-4567",
            eps_id="EPS001",
            habeas_data=True,
            custom_fields={
                "emergency_contact": "María Pérez - +57-300-987-6543",
                "allergies": ["Penicilina", "Polen"],
                "medical_conditions": ["Hipertensión"],
            },
            request_context={
                "tenant_id": str(tenant.id),
                "api_key_id": str(api_key.id),
                "request_id": "demo-seed-script"
            }
        )
        print(f"Created patient: {patient.first_name} {patient.first_last_name} (ID: {patient.id})")
        
        # Create sample appointment
        print("Creating sample appointment...")
        appointment_service = AppointmentService(db)
        appointment = await appointment_service.create_appointment(
            tenant_id=tenant.id,
            start_utc=datetime(2024, 2, 15, 10, 0, 0),
            end_utc=datetime(2024, 2, 15, 11, 0, 0),
            patient_document_type_id=1,
            patient_document_number="12345678",
            doctor_document_type_id=1,
            doctor_document_number="87654321",
            modality="IN_PERSON",
            state="SCHEDULED",
            appointment_type="CONSULTATION",
            clinic_id="CLINIC001",
            comment="Consulta de seguimiento",
            custom_fields={
                "room_number": "A-101",
                "specialty": "Cardiología",
                "priority": "Normal",
            },
            request_context={
                "tenant_id": str(tenant.id),
                "api_key_id": str(api_key.id),
                "request_id": "demo-seed-script"
            }
        )
        print(f"Created appointment: {appointment.id} for {appointment.start_utc}")
        
        print("\nDemo data created successfully!")
        print(f"Use this API key in the X-Api-Key header: {plaintext_key}")
        print(f"Sample patient document: {patient.document_number}")
        print(f"Sample appointment ID: {appointment.id}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_demo_data())
