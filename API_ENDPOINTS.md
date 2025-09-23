# Secre API - Complete Endpoint Reference

## Overview
This is a multi-tenant medical integration API with practical, easy-to-use endpoints for managing patients, appointments, and doctor availability.

## Authentication
All endpoints (except health checks) require API key authentication via the `X-Api-Key` header.

**Master API Key**: `hPoRkL0mz91Ui3sPTsFflbBUPvpHC67TdNC4ytGw19evzSRRlfn9To8LmL89b5wP`
**Miguel Parrado API Key**: `uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc`

## Base URL
- **Development**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

---

## 🏥 **Patients Management**

### Create Patient
```http
POST /v1/patients/
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "first_name": "Ana",
  "first_last_name": "García",
  "birth_date": "1988-12-05",
  "gender_id": 2,
  "document_type_id": 1,
  "document_number": "11223399",
  "phone": "3001112222",
  "cell_phone": "3001112222",
  "email": "ana.garcia@example.com",
  "eps_id": "EPS004",
  "habeas_data": true,
  "custom_fields": {
    "emergency_contact": "Luis García",
    "emergency_phone": "3003334444"
  }
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

### List Patients
```http
GET /v1/patients/?page=1&size=50&document_type_id=1&document_number=11223399
X-Api-Key: {your_api_key}
```

### Update Patient
```http
PATCH /v1/patients/{patient_id}
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "phone": "3009998888",
  "email": "ana.garcia.updated@example.com"
}
```

### Delete Patient
```http
DELETE /v1/patients/{patient_id}
X-Api-Key: {your_api_key}
```

---

## 📅 **Appointments Management**

### Create Appointment
```http
POST /v1/appointments/
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "start_datetime": "2025-09-25T10:00:00",
  "end_datetime": "2025-09-25T11:00:00",
  "patient_document_type_id": 1,
  "patient_document_number": "11223399",
  "doctor_document_type_id": 1,
  "doctor_document_number": "99999999",
  "modality": "presencial",
  "state": "scheduled",
  "appointment_type": "consulta",
  "clinic_id": "CLINIC001",
  "comment": "Consulta de seguimiento",
  "custom_fields": {
    "room": "A101",
    "specialty": "Medicina General"
  }
}
```

### Get Appointment by ID
```http
GET /v1/appointments/{appointment_id}
X-Api-Key: {your_api_key}
```

### List Appointments
```http
GET /v1/appointments/?page=1&size=50&start_date=2025-09-25&end_date=2025-09-26
X-Api-Key: {your_api_key}
```

### Get Appointments by Date Range
```http
GET /v1/appointments/by-date-range?start_date=2025-09-25&end_date=2025-09-26&limit=100
X-Api-Key: {your_api_key}
```

### Update Appointment
```http
PATCH /v1/appointments/{appointment_id}
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "state": "completed",
  "comment": "Consulta completada exitosamente"
}
```

### Delete Appointment
```http
DELETE /v1/appointments/{appointment_id}
X-Api-Key: {your_api_key}
```

---

## 👨‍⚕️ **Doctor Availability & Calendar**

### Set Doctor Work Hours
```http
POST /v1/doctor-availability/availability
Content-Type: application/json
X-Api-Key: {your_api_key}

{
  "doctor_document_type_id": 1,
  "doctor_document_number": "99999999",
  "day_of_week": 3,
  "start_time": "09:00",
  "end_time": "17:00",
  "appointment_duration_minutes": 30,
  "custom_fields": {
    "specialty": "Medicina General"
  }
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
  "doctor_document_number": "99999999",
  "start_datetime": "2025-09-25T12:00:00",
  "end_datetime": "2025-09-25T13:00:00",
  "reason": "Lunch break"
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
  "start_datetime": "2025-09-25T12:30:00",
  "end_datetime": "2025-09-25T13:30:00",
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
GET /v1/doctor-availability/time-slots/{doctor_document_type_id}/{doctor_document_number}?date=2025-09-25
X-Api-Key: {your_api_key}
```

**Response Example**:
```json
{
  "doctor_document_type_id": 1,
  "doctor_document_number": "99999999",
  "date": "2025-09-25",
  "time_slots": [
    {
      "start_datetime": "2025-09-25T09:00:00",
      "end_datetime": "2025-09-25T09:30:00",
      "available": true
    },
    {
      "start_datetime": "2025-09-25T10:00:00",
      "end_datetime": "2025-09-25T10:30:00",
      "available": false
    }
  ],
  "total_slots": 16,
  "available_slots": 14
}
```

### Check Time Availability
```http
GET /v1/doctor-availability/check-availability/{doctor_document_type_id}/{doctor_document_number}?start_datetime=2025-09-25T10:00:00&end_datetime=2025-09-25T11:00:00
X-Api-Key: {your_api_key}
```

---

## 🏢 **Admin & Tenant Management**

### Create Tenant (Master Key Required)
```http
POST /v1/admin/tenants
Content-Type: application/json
X-Api-Key: {master_api_key}

{
  "name": "Miguel Parrado"
}
```

### Bootstrap System (Master Key Required)
```http
POST /v1/admin/bootstrap
X-Api-Key: {master_api_key}
```

---

## 🔑 **Authentication & API Keys**

### List API Keys
```http
GET /v1/auth/api-keys
X-Api-Key: {your_api_key}
```

### Get API Key by ID
```http
GET /v1/auth/api-keys/{api_key_id}
X-Api-Key: {your_api_key}
```

### Revoke API Key
```http
POST /v1/auth/api-keys/{api_key_id}/revoke
X-Api-Key: {your_api_key}
```

### List Tenants
```http
GET /v1/auth/tenants
X-Api-Key: {your_api_key}
```

### Get Tenant by ID
```http
GET /v1/auth/tenants/{tenant_id}
X-Api-Key: {your_api_key}
```

---

## 📊 **Lookup Data**

### Get Document Types
```http
GET /v1/lookup/document-types
X-Api-Key: {your_api_key}
```

### Get Genders
```http
GET /v1/lookup/genders
X-Api-Key: {your_api_key}
```

### Get Appointment Modalities
```http
GET /v1/lookup/appointment-modalities
X-Api-Key: {your_api_key}
```

### Get Appointment States
```http
GET /v1/lookup/appointment-states
X-Api-Key: {your_api_key}
```

---

## 🏥 **Health Checks**

### Basic Health Check
```http
GET /health
```

### Detailed Health Check
```http
GET /v1/health/
```

---

## 📝 **Data Formats**

### Date Formats
- **Birth Date**: `YYYY-MM-DD` (e.g., `1988-12-05`)
- **DateTime**: `YYYY-MM-DDTHH:MM:SS` (e.g., `2025-09-25T10:00:00`)
- **Time**: `HH:MM` (e.g., `09:00`)

### Day of Week
- `0` = Monday
- `1` = Tuesday
- `2` = Wednesday
- `3` = Thursday
- `4` = Friday
- `5` = Saturday
- `6` = Sunday

### Document Types
- `1` = Cédula de Ciudadanía
- `2` = Cédula de Extranjería
- `3` = Pasaporte
- `4` = Tarjeta de Identidad

### Genders
- `1` = Masculino
- `2` = Femenino
- `3` = Otro

---

## 🚀 **Quick Start Examples**

### 1. Create a Patient
```bash
curl -X POST http://localhost:8000/v1/patients/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc" \
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
  -H "X-Api-Key: uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc" \
  -d '{
    "doctor_document_type_id": 1,
    "doctor_document_number": "99999999",
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
  -H "X-Api-Key: uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc" \
  -d '{
    "start_datetime": "2025-09-25T10:00:00",
    "end_datetime": "2025-09-25T11:00:00",
    "patient_document_type_id": 1,
    "patient_document_number": "12345678",
    "doctor_document_type_id": 1,
    "doctor_document_number": "99999999",
    "modality": "presencial",
    "state": "scheduled"
  }'
```

### 4. Check Available Time Slots
```bash
curl -X GET "http://localhost:8000/v1/doctor-availability/time-slots/1/99999999?date=2025-09-25" \
  -H "X-Api-Key: uvG1t0H6xS4_qKkd1qMmMKlH0AbtShBBqo0GaZCbwjc"
```

---

## 🔒 **Security Notes**

- All API keys are tenant-specific and provide access only to that tenant's data
- The master API key should be kept secure and only used for administrative operations
- All endpoints enforce tenant isolation at the database level
- Sensitive operations require proper authentication

## 📈 **Best Practices**

1. **Use PATCH for updates** - Only send the fields you want to change
2. **Check availability before creating appointments** - Use the time slots endpoint
3. **Use document-based lookups** - More efficient than ID-based searches
4. **Set up doctor availability first** - Before creating appointments
5. **Use pagination** - For large result sets, use `page` and `size` parameters
6. **Handle errors gracefully** - Check HTTP status codes and error messages
7. **Keep API keys secure** - Don't expose them in client-side code
