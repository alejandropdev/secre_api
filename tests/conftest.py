"""Pytest configuration and fixtures."""

import asyncio
import os
import uuid
from datetime import date, datetime, timedelta
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.api_key import ApiKey
from app.models.tenant import Tenant
from app.core.security import hash_api_key


# Test database URL - use a separate test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/secre_test"
)

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Clean up tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def test_client(test_db: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_test_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None, None]:
    """Create an async test client with database override."""
    
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_tenant(test_db: AsyncSession) -> AsyncGenerator[Tenant, None, None]:
    """Create a test tenant."""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Tenant",
        is_active=True
    )
    test_db.add(tenant)
    await test_db.commit()
    await test_db.refresh(tenant)
    yield tenant


@pytest_asyncio.fixture(scope="function")
async def test_tenant_2(test_db: AsyncSession) -> AsyncGenerator[Tenant, None, None]:
    """Create a second test tenant for isolation testing."""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Tenant 2",
        is_active=True
    )
    test_db.add(tenant)
    await test_db.commit()
    await test_db.refresh(tenant)
    yield tenant


@pytest_asyncio.fixture(scope="function")
async def test_api_key(test_db: AsyncSession, test_tenant: Tenant) -> AsyncGenerator[ApiKey, None, None]:
    """Create a test API key."""
    api_key = ApiKey(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        key_hash=hash_api_key("test-api-key-123"),
        name="Test API Key",
        last_used_at=datetime.utcnow()
    )
    test_db.add(api_key)
    await test_db.commit()
    await test_db.refresh(api_key)
    yield api_key


@pytest_asyncio.fixture(scope="function")
async def test_api_key_2(test_db: AsyncSession, test_tenant_2: Tenant) -> AsyncGenerator[ApiKey, None, None]:
    """Create a second test API key for isolation testing."""
    api_key = ApiKey(
        id=uuid.uuid4(),
        tenant_id=test_tenant_2.id,
        key_hash=hash_api_key("test-api-key-456"),
        name="Test API Key 2",
        last_used_at=datetime.utcnow()
    )
    test_db.add(api_key)
    await test_db.commit()
    await test_db.refresh(api_key)
    yield api_key


@pytest.fixture
def auth_headers(test_api_key: ApiKey) -> dict:
    """Get authentication headers for test API key."""
    return {"X-Api-Key": "test-api-key-123"}


@pytest.fixture
def auth_headers_2(test_api_key_2: ApiKey) -> dict:
    """Get authentication headers for second test API key."""
    return {"X-Api-Key": "test-api-key-456"}


@pytest.fixture
def sample_patient_data() -> dict:
    """Sample patient data for testing."""
    return {
        "eventType": "PATIENT",
        "actionType": "CREATE",
        "firstName": "Juan",
        "firstLastName": "Pérez",
        "secondName": "Carlos",
        "secondLastName": "González",
        "birthDate": "1990-05-15",
        "genderId": 1,
        "documentTypeId": 1,
        "documentNumber": "12345678",
        "phone": "+57-1-234-5678",
        "cellPhone": "+57-300-123-4567",
        "email": "juan.perez@example.com",
        "epsId": "EPS001",
        "habeasData": True,
        "customFields": {
            "emergencyContact": "María González",
            "emergencyPhone": "+57-300-987-6543"
        }
    }


@pytest.fixture
def sample_appointment_data() -> dict:
    """Sample appointment data for testing."""
    return {
        "eventType": "APPOINTMENT",
        "actionType": "CREATE",
        "startAppointment": "2024-01-15T10:00:00-05:00",
        "endAppointment": "2024-01-15T11:00:00-05:00",
        "patientDocumentTypeId": 1,
        "patientDocumentNumber": "12345678",
        "doctorDocumentTypeId": 1,
        "doctorDocumentNumber": "87654321",
        "modality": "presencial",
        "state": "scheduled",
        "notificationState": "pending",
        "appointmentType": "consulta_general",
        "clinicId": "CLINIC001",
        "comment": "Consulta de rutina",
        "customFields": {
            "room": "A101",
            "specialInstructions": "Paciente alérgico a penicilina"
        }
    }


@pytest.fixture
def invalid_patient_data() -> dict:
    """Invalid patient data for testing validation."""
    return {
        "eventType": "PATIENT",
        "actionType": "CREATE",
        "firstName": "",  # Invalid: empty name
        "firstLastName": "Pérez",
        "birthDate": "invalid-date",  # Invalid date format
        "genderId": 999,  # Invalid gender ID
        "documentTypeId": 1,
        "documentNumber": "",  # Invalid: empty document
    }


@pytest.fixture
def invalid_appointment_data() -> dict:
    """Invalid appointment data for testing validation."""
    return {
        "eventType": "APPOINTMENT",
        "actionType": "CREATE",
        "startAppointment": "2024-01-15T11:00:00-05:00",  # End before start
        "endAppointment": "2024-01-15T10:00:00-05:00",
        "patientDocumentTypeId": 1,
        "patientDocumentNumber": "12345678",
        "doctorDocumentTypeId": 1,
        "doctorDocumentNumber": "87654321",
        "modality": "invalid_modality",  # Invalid modality
        "state": "invalid_state",  # Invalid state
    }
