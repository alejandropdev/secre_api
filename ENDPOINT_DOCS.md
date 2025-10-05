# Secre API - Complete Endpoint Documentation

## Overview

The Secre API is a multi-tenant medical integration API built with FastAPI, PostgreSQL, and Row Level Security (RLS). It provides comprehensive endpoints for managing patients, appointments, doctor availability, and tenant administration.

## Table of Contents

1. [Authentication](#authentication)
2. [Getting Started](#getting-started)
3. [Tenant Management](#tenant-management)
4. [API Key Management](#api-key-management)
5. [Patient Management](#patient-management)
6. [Appointment Management](#appointment-management)
7. [Doctor Availability Management](#doctor-availability-management)
8. [Lookup Data](#lookup-data)
9. [Health Checks](#health-checks)
10. [Data Validation & Normalization](#data-validation--normalization)
11. [Error Handling](#error-handling)
12. [Best Practices](#best-practices)

---

## Authentication

All endpoints (except health checks and bootstrap) require API key authentication via the `X-Api-Key` header.

### Master API Key
- **Key**: `hPoRkL0mz91Ui3sPTsFflbBUPvpHC67TdNC4ytGw19evzSRRlfn9To8LmL89b5wP`
- **Usage**: Required for admin operations (tenant creation, system bootstrap)
- **Security**: Keep this key secure and only use for administrative operations

### Tenant API Keys
- **Format**: Generated automatically when creating tenants
- **Scope**: Tenant-specific access only
- **Security**: Each tenant's data is isolated at the database level

### Example Authentication
```bash
curl -H "X-Api-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/v1/patients/
```

---

## Getting Started

### 1. System Bootstrap (First Time Setup)

If this is the first time setting up the system, use the bootstrap endpoint:

```bash
curl -X POST "http://localhost:8000/v1/admin/bootstrap" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Your Medical Center"
     }'
```

**Response:**
```json
{
  "api_key": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Bootstrap API Key",
    "last_used_at": null,
    "created_at": "2024-01-15T10:30:00Z",
    "revoked_at": null
  },
  "plaintext_key": "your-generated-api-key-here"
}
```

### 2. Create Additional Tenants (Admin Only)

```bash
curl -X POST "http://localhost:8000/v1/admin/tenants" \
     -H "Content-Type: application/json" \
     -H "X-Api-Key: hPoRkL0mz91Ui3sPTsFflbBUPvpHC67TdNC4ytGw19evzSRRlfn9To8LmL89b5wP" \
     -d '{
       "name": "Another Medical Center"
     }'
```

---

## Tenant Management

### Create Tenant
```http
POST /v1/auth/tenants
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "name": "Medical Center Name"
}
```

### List Tenants
```http
GET /v1/auth/tenants?page=1&size=50
X-Api-Key: {your_api_key}
```

### Get Tenant by ID
```http
GET /v1/auth/tenants/{tenant_id}
X-Api-Key: {your_api_key}
```

### Update Tenant
```http
PATCH /v1/auth/tenants/{tenant_id}
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "name": "Updated Medical Center Name",
  "is_active": true
}
```

---

## API Key Management

### Create API Key
```http
POST /v1/auth/api-keys
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "name": "API Key Name",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Response:**
```json
{
  "api_key": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "API Key Name",
    "last_used_at": null,
    "created_at": "2024-01-15T10:30:00Z",
    "revoked_at": null
  },
  "plaintext_key": "your-generated-api-key-here"
}
```

### List API Keys
```http
GET /v1/auth/api-keys?tenant_id={tenant_id}&page=1&size=50
X-Api-Key: {your_api_key}
```

**Query Parameters:**
- `tenant_id`: (Optional) Specific tenant ID to list API keys for. If not provided:
  - **Master API Key**: Lists all API keys across all tenants
  - **Regular API Key**: Lists API keys for the current tenant only
- `page`: Page number (default: 1)
- `size`: Page size (default: 50, max: 100)

**Master API Key Behavior:**
- Without `tenant_id`: Returns all API keys across all tenants
- With `tenant_id`: Returns API keys for the specified tenant

**Regular API Key Behavior:**
- Without `tenant_id`: Returns API keys for the current tenant
- With `tenant_id`: Returns API keys for the specified tenant (if authorized)

### Revoke API Key
```http
POST /v1/auth/api-keys/{api_key_id}/revoke
X-Api-Key: {your_api_key}
```

### Get API Key Usage Statistics
```http
GET /v1/auth/api-keys/{api_key_id}/usage?days=30
X-Api-Key: {your_api_key}
```

**Query Parameters:**
- `days`: Number of days to include in statistics (default: 30, max: 365)

**Response:**
```json
{
  "stats": {
    "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
    "period_days": 30,
    "start_date": "2024-01-15",
    "end_date": "2024-02-14",
    "total_requests": 1250,
    "endpoint_stats": [
      {
        "endpoint": "/v1/patients/",
        "method": "POST",
        "total_requests": 450,
        "avg_response_time_ms": 125.5
      },
      {
        "endpoint": "/v1/appointments/",
        "method": "GET",
        "total_requests": 320,
        "avg_response_time_ms": 89.2
      }
    ],
    "status_stats": [
      {
        "status_code": 200,
        "total_requests": 1100
      },
      {
        "status_code": 201,
        "total_requests": 150
      }
    ],
    "daily_usage": [
      {
        "date": "2024-02-14",
        "total_requests": 45
      },
      {
        "date": "2024-02-13",
        "total_requests": 52
      }
    ],
    "hourly_usage": [
      {
        "hour": 9,
        "total_requests": 120
      },
      {
        "hour": 10,
        "total_requests": 180
      }
    ]
  },
  "generated_at": "2024-02-15T10:30:00Z"
}
```

### Get Tenant Usage Statistics
```http
GET /v1/auth/tenants/{tenant_id}/usage?days=30
X-Api-Key: {your_api_key}
```

**Query Parameters:**
- `days`: Number of days to include in statistics (default: 30, max: 365)

**Response:**
```json
{
  "stats": {
    "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    "period_days": 30,
    "start_date": "2024-01-15",
    "end_date": "2024-02-14",
    "total_requests": 2500,
    "api_key_stats": [
      {
        "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
        "total_requests": 1250,
        "avg_response_time_ms": 98.5
      },
      {
        "api_key_id": "550e8400-e29b-41d4-a716-446655440002",
        "total_requests": 800,
        "avg_response_time_ms": 112.3
      }
    ]
  },
  "generated_at": "2024-02-15T10:30:00Z"
}
```

### Get Top Endpoints by Usage
```http
GET /v1/auth/usage/top-endpoints?days=7&limit=10
X-Api-Key: {your_api_key}
```

**Query Parameters:**
- `days`: Number of days to analyze (default: 7, max: 30)
- `limit`: Maximum number of endpoints to return (default: 10, max: 50)

**Behavior:**
- **Master API Key**: Returns top endpoints across all tenants
- **Regular API Key**: Returns top endpoints for the current tenant only

**Response:**
```json
{
  "endpoints": [
    {
      "endpoint": "/v1/patients/",
      "method": "POST",
      "total_requests": 1250,
      "avg_response_time_ms": 125.5
    },
    {
      "endpoint": "/v1/appointments/",
      "method": "GET",
      "total_requests": 980,
      "avg_response_time_ms": 89.2
    },
    {
      "endpoint": "/v1/doctor-availability/time-slots/",
      "method": "GET",
      "total_requests": 750,
      "avg_response_time_ms": 156.8
    }
  ],
  "period_days": 7,
  "generated_at": "2024-02-15T10:30:00Z"
}
```

---

## Patient Management

### Create Patient
```http
POST /v1/patients/
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "first_name": "Juan",
  "first_last_name": "Pérez",
  "second_name": "Carlos",
  "second_last_name": "González",
  "birth_date": "1990-05-15",
  "gender_id": 1,
  "document_type_id": 1,
  "document_number": "12345678",
  "phone": "+57-300-123-4567",
  "email": "juan.perez@example.com",
  "eps_id": "EPS001",
  "habeas_data": true,
  "custom_fields": {
    "emergency_contact": "María Pérez - +57-300-987-6543",
    "allergies": ["Penicilina", "Polen"],
    "medical_conditions": ["Hipertensión"],
    "blood_type": "O+",
    "insurance": {
      "provider": "EPS Sanitas",
      "policy_number": "POL-123456789"
    }
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
  "first_name": "Juan",
  "second_name": "Carlos",
  "first_last_name": "Pérez",
  "second_last_name": "González",
  "birth_date": "1990-05-15",
  "gender_id": 1,
  "document_type_id": 1,
  "document_number": "12345678",
  "phone": "+573001234567",
  "email": "juan.perez@example.com",
  "eps_id": "EPS001",
  "habeas_data": true,
  "custom_fields": {
    "emergency_contact": "María Pérez - +57-300-987-6543",
    "allergies": ["Penicilina", "Polen"],
    "medical_conditions": ["Hipertensión"],
    "blood_type": "O+",
    "insurance": {
      "provider": "EPS Sanitas",
      "policy_number": "POL-123456789"
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get Patient by ID
```http
GET /v1/patients/{patient_id}
X-Api-Key: {your_api_key}
```

### Get Patient by Document
```http
GET /v1/patients/by-document/{document_type_id}/{document_number}
X-Api-Key: {your_api_key}
```

### Search Patients
```http
GET /v1/patients/search?document_type_id=1&document_number=12345678&page=1&size=50
X-Api-Key: {your_api_key}
```

**Query Parameters:**
- `document_type_id`: Filter by document type ID
- `document_number`: Filter by document number
- `email`: Filter by email
- `phone`: Filter by phone
- `page`: Page number (default: 1)
- `size`: Page size (default: 50, max: 100)

### Update Patient
```http
PATCH /v1/patients/{patient_id}
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "phone": "+57-300-999-8888",
  "email": "juan.perez.updated@example.com",
  "custom_fields": {
    "emergency_contact": "María Pérez - +57-300-987-6543",
    "allergies": ["Penicilina", "Polen", "Aspirina"],
    "medical_conditions": ["Hipertensión", "Diabetes"]
  }
}
```

### Delete Patient
```http
DELETE /v1/patients/{patient_id}
X-Api-Key: {your_api_key}
```

---

## Appointment Management

### Create Appointment
```http
POST /v1/appointments/
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "start_datetime": "2024-02-15T10:00:00",
  "end_datetime": "2024-02-15T11:00:00",
  "patient_document_type_id": 1,
  "patient_document_number": "12345678",
  "doctor_document_type_id": 1,
  "doctor_document_number": "87654321",
  "modality_id": 1,
  "state_id": 1,
  "appointment_type_id": 1,
  "clinic_id": 1,
  "comment": "Consulta de seguimiento",
  "custom_fields": {
    "room": "A101",
    "specialty": "Cardiología",
    "priority": "Normal",
    "equipment_needed": ["ECG", "Blood pressure monitor"],
    "notes": "Patient prefers morning appointments"
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
  "start_utc": "2024-02-15T10:00:00Z",
  "end_utc": "2024-02-15T11:00:00Z",
  "patient_document_type_id": 1,
  "patient_document_number": "12345678",
  "doctor_document_type_id": 1,
  "doctor_document_number": "87654321",
  "modality_id": 1,
  "state_id": 1,
  "notification_state": "pending",
  "appointment_type_id": 1,
  "clinic_id": 1,
  "comment": "Consulta de seguimiento",
  "custom_fields": {
    "room": "A101",
    "specialty": "Cardiología",
    "priority": "Normal",
    "equipment_needed": ["ECG", "Blood pressure monitor"],
    "notes": "Patient prefers morning appointments"
  },
  "modality_name": "Presencial",
  "state_name": "Programada",
  "appointment_type_name": "Consulta",
  "clinic_name": "Clínica Principal",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get Appointment by ID
```http
GET /v1/appointments/{appointment_id}
X-Api-Key: {your_api_key}
```

### Search Appointments
```http
GET /v1/appointments/?start_date=2024-02-01T00:00:00&end_date=2024-02-29T23:59:59&modality_id=1&state_id=1&page=1&size=50
X-Api-Key: {your_api_key}
```

**Query Parameters:**
- `start_date`: Filter by start date
- `end_date`: Filter by end date
- `modality_id`: Filter by modality ID
- `state_id`: Filter by state ID
- `patient_document_number`: Filter by patient document number
- `doctor_document_number`: Filter by doctor document number
- `page`: Page number (default: 1)
- `size`: Page size (default: 50, max: 100)

### Get Appointments by Date Range
```http
GET /v1/appointments/by-date-range?start_date=2024-02-01T00:00:00&end_date=2024-02-29T23:59:59&limit=100&offset=0
X-Api-Key: {your_api_key}
```

### Update Appointment
```http
PATCH /v1/appointments/{appointment_id}
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "state_id": 2,
  "comment": "Consulta completada exitosamente",
  "custom_fields": {
    "room": "A102",
    "specialty": "Cardiología",
    "priority": "High",
    "equipment_needed": ["ECG", "Blood pressure monitor", "Echocardiogram"],
    "notes": "Patient confirmed, prefers morning appointments",
    "insurance_verified": true,
    "copay_amount": 5000
  }
}
```

### Delete Appointment
```http
DELETE /v1/appointments/{appointment_id}
X-Api-Key: {your_api_key}
```

---

## Doctor Availability Management

### Set Doctor Work Hours
```http
POST /v1/doctor-availability/availability
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "doctor_document_type_id": 1,
  "doctor_document_number": "87654321",
  "day_of_week": 1,
  "start_time": "09:00",
  "end_time": "17:00",
  "appointment_duration_minutes": 30,
  "custom_fields": {
    "specialty": "Medicina General",
    "location": "Consultorio A"
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
  "doctor_document_type_id": 1,
  "doctor_document_number": "87654321",
  "day_of_week": 1,
  "start_time": "09:00",
  "end_time": "17:00",
  "appointment_duration_minutes": 30,
  "is_active": true,
  "custom_fields": {
    "specialty": "Medicina General",
    "location": "Consultorio A"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get Doctor Availability
```http
GET /v1/doctor-availability/availability/{doctor_document_type_id}/{doctor_document_number}
X-Api-Key: {your_api_key}
```

### Update Doctor Availability
```http
PATCH /v1/doctor-availability/availability/{availability_id}
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "start_time": "08:00",
  "end_time": "18:00",
  "appointment_duration_minutes": 45
}
```

### Delete Doctor Availability
```http
DELETE /v1/doctor-availability/availability/{availability_id}
X-Api-Key: {your_api_key}
```

### Block Time Slots
```http
POST /v1/doctor-availability/blocked-time
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "doctor_document_type_id": 1,
  "doctor_document_number": "87654321",
  "start_datetime": "2024-02-15T12:00:00",
  "end_datetime": "2024-02-15T13:00:00",
  "reason": "Lunch break",
  "custom_fields": {
    "type": "personal",
    "recurring": false
  }
}
```

### Get Blocked Times
```http
GET /v1/doctor-availability/blocked-time/{doctor_document_type_id}/{doctor_document_number}
X-Api-Key: {your_api_key}
```

### Update Blocked Time
```http
PATCH /v1/doctor-availability/blocked-time/{blocked_time_id}
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "start_datetime": "2024-02-15T12:30:00",
  "end_datetime": "2024-02-15T13:30:00",
  "reason": "Extended lunch break"
}
```

### Delete Blocked Time
```http
DELETE /v1/doctor-availability/blocked-time/{blocked_time_id}
X-Api-Key: {your_api_key}
```

### Get Available Time Slots
```http
GET /v1/doctor-availability/time-slots/{doctor_document_type_id}/{doctor_document_number}?date=2024-02-15
X-Api-Key: {your_api_key}
```

**Response:**
```json
{
  "doctor_document_type_id": 1,
  "doctor_document_number": "87654321",
  "date": "2024-02-15",
  "time_slots": [
    {
      "start_datetime": "2024-02-15T09:00:00Z",
      "end_datetime": "2024-02-15T09:30:00Z",
      "available": true
    },
    {
      "start_datetime": "2024-02-15T09:30:00Z",
      "end_datetime": "2024-02-15T10:00:00Z",
      "available": true
    },
    {
      "start_datetime": "2024-02-15T10:00:00Z",
      "end_datetime": "2024-02-15T10:30:00Z",
      "available": false
    }
  ],
  "total_slots": 16,
  "available_slots": 14
}
```

### Check Time Availability
```http
GET /v1/doctor-availability/check-availability/{doctor_document_type_id}/{doctor_document_number}?start_datetime=2024-02-15T10:00:00&end_datetime=2024-02-15T11:00:00
X-Api-Key: {your_api_key}
```

**Response:**
```json
{
  "available": true,
  "doctor_document_type_id": 1,
  "doctor_document_number": "87654321",
  "start_datetime": "2024-02-15T10:00:00Z",
  "end_datetime": "2024-02-15T11:00:00Z"
}
```

---

## Lookup Data

### Get Document Types
```http
GET /v1/lookup/document-types
X-Api-Key: {your_api_key}
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Cédula de Ciudadanía",
      "code": "CC",
      "description": "Documento de identidad colombiano"
    },
    {
      "id": 2,
      "name": "Cédula de Extranjería",
      "code": "CE",
      "description": "Documento de identidad para extranjeros"
    },
    {
      "id": 3,
      "name": "Pasaporte",
      "code": "PA",
      "description": "Pasaporte internacional"
    },
    {
      "id": 4,
      "name": "Tarjeta de Identidad",
      "code": "TI",
      "description": "Tarjeta de identidad para menores"
    }
  ],
  "total": 4
}
```

### Get Genders
```http
GET /v1/lookup/genders
X-Api-Key: {your_api_key}
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Masculino",
      "code": "M",
      "description": "Género masculino"
    },
    {
      "id": 2,
      "name": "Femenino",
      "code": "F",
      "description": "Género femenino"
    },
    {
      "id": 3,
      "name": "Otro",
      "code": "O",
      "description": "Otro género"
    }
  ],
  "total": 3
}
```

### Get Appointment Modalities
```http
GET /v1/lookup/appointment-modalities
X-Api-Key: {your_api_key}
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Presencial",
      "code": "PRESENCIAL",
      "description": "Cita presencial en consultorio"
    },
    {
      "id": 2,
      "name": "Virtual",
      "code": "VIRTUAL",
      "description": "Cita virtual por videollamada"
    },
    {
      "id": 3,
      "name": "Telefónica",
      "code": "TELEFONICA",
      "description": "Cita por teléfono"
    },
    {
      "id": 4,
      "name": "Domicilio",
      "code": "DOMICILIO",
      "description": "Visita médica a domicilio"
    }
  ],
  "total": 4
}
```

### Get Appointment States
```http
GET /v1/lookup/appointment-states
X-Api-Key: {your_api_key}
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Programada",
      "code": "PROGRAMADA",
      "description": "Cita programada"
    },
    {
      "id": 2,
      "name": "Confirmada",
      "code": "CONFIRMADA",
      "description": "Cita confirmada por el paciente"
    },
    {
      "id": 3,
      "name": "En Progreso",
      "code": "EN_PROGRESO",
      "description": "Cita en curso"
    },
    {
      "id": 4,
      "name": "Completada",
      "code": "COMPLETADA",
      "description": "Cita completada"
    },
    {
      "id": 5,
      "name": "Cancelada",
      "code": "CANCELADA",
      "description": "Cita cancelada"
    },
    {
      "id": 6,
      "name": "No Asistió",
      "code": "NO_ASISTIO",
      "description": "Paciente no asistió"
    }
  ],
  "total": 6
}
```

---

## Health Checks

### Basic Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Detailed Health Check
```http
GET /v1/health/
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime": 3600.5,
  "database": "healthy"
}
```

---

## API Usage Tracking

The API automatically tracks usage metrics for all requests to provide comprehensive analytics and monitoring capabilities.

### Automatic Tracking

Every API request is automatically tracked with the following information:
- **API Key ID**: Which API key was used
- **Tenant ID**: Which tenant made the request
- **Endpoint**: The API endpoint accessed
- **HTTP Method**: GET, POST, PATCH, DELETE, etc.
- **Status Code**: Response status code
- **Response Time**: Request processing time in milliseconds
- **Timestamp**: When the request was made
- **Client IP**: IP address of the client
- **User Agent**: Client user agent string

### Usage Statistics Available

#### Per API Key Statistics
- Total requests over time periods
- Requests by endpoint and method
- Requests by status code
- Daily usage patterns
- Hourly usage patterns
- Average response times

#### Per Tenant Statistics
- Total requests across all API keys
- Usage breakdown by API key
- Tenant-wide performance metrics

#### System-wide Analytics
- Top endpoints by usage
- Most active API keys
- Performance trends

### Data Retention

- **Usage records**: Kept for 90 days by default
- **Aggregated statistics**: Available for up to 1 year
- **Automatic cleanup**: Old records are automatically removed

### Privacy & Security

- **IP addresses**: Stored for security and analytics
- **User agents**: Stored for debugging and analytics
- **Tenant isolation**: Usage data is isolated by tenant
- **No sensitive data**: Only metadata is tracked, not request/response content

---

## Data Validation & Normalization

The API includes comprehensive validation and normalization features:

### Document Number Validation
- **CC (Cédula de Ciudadanía)**: 6-10 digits
- **CE (Cédula de Extranjería)**: 6-10 digits
- **TI (Tarjeta de Identidad)**: 6-10 digits
- **RC (Registro Civil)**: 2 letters + 6-10 digits
- **PA (Pasaporte)**: 2 letters + 6-10 digits

### Phone Number Validation
- Supports Colombian phone number formats
- Automatically adds `+57` prefix if missing
- Normalizes to `+57XXXXXXXXXX` format

### Email Validation
- Standard email format validation
- Converts to lowercase
- Trims whitespace

### Date and Time Validation
- **Birth Date**: Cannot be in the future, max 150 years ago
- **Appointment DateTime**: RFC3339 format with timezone support
- **Time Validation**: End time must be after start time

### Custom Fields Validation
- Maximum 50 custom fields per record
- Maximum 100 characters for field names
- Maximum 1000 characters for field values
- Maximum nesting depth of 3 levels

---

## Error Handling

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `401`: Unauthorized (invalid API key)
- `404`: Not Found
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

### Error Response Format
```json
{
  "detail": [
    {
      "loc": ["body", "document_number"],
      "msg": "Invalid document number format for type 1",
      "type": "value_error"
    }
  ]
}
```

### Common Validation Errors
- `"Invalid document number format for type {type_id}"`
- `"Invalid phone number format"`
- `"Invalid email format"`
- `"Birth date cannot be in the future"`
- `"Appointment start time cannot be in the past"`
- `"End time must be after start time"`

---

## Best Practices

### 1. Authentication
- Always include the `X-Api-Key` header
- Keep API keys secure and don't expose them in client-side code
- Use the master API key only for administrative operations

### 2. Data Management
- Use PATCH for updates (only send fields you want to change)
- Check availability before creating appointments
- Use document-based lookups for better performance
- Set up doctor availability before creating appointments

### 3. Pagination
- Use `page` and `size` parameters for large result sets
- Default page size is 50, maximum is 100
- Check `has_next` and `has_prev` for navigation

### 4. Custom Fields
- Keep custom fields simple and avoid deep nesting
- Use consistent naming conventions
- Document custom field schemas for your team

### 5. Error Handling
- Always check HTTP status codes
- Handle validation errors gracefully
- Provide user-friendly error messages

### 6. Performance
- Use specific endpoints (e.g., by-document) instead of search when possible
- Implement proper caching for lookup data
- Use date range queries for appointment searches

---

## Quick Start Examples

### 1. Create a Patient
```bash
curl -X POST http://localhost:8000/v1/patients/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your-api-key" \
  -d '{
    "first_name": "Juan",
    "first_last_name": "Pérez",
    "birth_date": "1990-05-15",
    "gender_id": 1,
    "document_type_id": 1,
    "document_number": "12345678",
    "phone": "3001234567",
    "email": "juan.perez@example.com"
  }'
```

### 2. Set Doctor Availability
```bash
curl -X POST http://localhost:8000/v1/doctor-availability/availability \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your-api-key" \
  -d '{
    "doctor_document_type_id": 1,
    "doctor_document_number": "87654321",
    "day_of_week": 1,
    "start_time": "09:00",
    "end_time": "17:00",
    "appointment_duration_minutes": 30
  }'
```

### 3. Create an Appointment
```bash
curl -X POST http://localhost:8000/v1/appointments/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your-api-key" \
  -d '{
    "start_datetime": "2024-02-15T10:00:00",
    "end_datetime": "2024-02-15T11:00:00",
    "patient_document_type_id": 1,
    "patient_document_number": "12345678",
    "doctor_document_type_id": 1,
    "doctor_document_number": "87654321",
    "modality_id": 1,
    "state_id": 1
  }'
```

### 4. Check Available Time Slots
```bash
curl -X GET "http://localhost:8000/v1/doctor-availability/time-slots/1/87654321?date=2024-02-15" \
  -H "X-Api-Key: your-api-key"
```

---

## Security Notes

- All API keys are tenant-specific and provide access only to that tenant's data
- The master API key should be kept secure and only used for administrative operations
- All endpoints enforce tenant isolation at the database level using Row Level Security (RLS)
- Sensitive operations require proper authentication
- All data is validated and normalized before storage
- Audit trails are maintained for all data modifications

---

## Support

For technical support or questions about the API, please refer to the project documentation or contact the development team.

**API Version**: 1.0.0  
**Last Updated**: January 2024
