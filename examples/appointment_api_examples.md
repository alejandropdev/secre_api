# Appointment API Examples

This document provides comprehensive examples of how to use the Appointment CRUD endpoints.

## Authentication

All appointment endpoints require API key authentication via the `X-Api-Key` header.

```bash
curl -H "X-Api-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     https://api.secre.com/v1/appointments/
```

## 1. Create Appointment

### Request
```bash
curl -X POST "https://api.secre.com/v1/appointments/" \
     -H "X-Api-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{
       "eventType": "APPOINTMENT",
       "actionType": "CREATE",
       "startAppointment": "2024-02-15T10:00:00Z",
       "endAppointment": "2024-02-15T11:00:00Z",
       "patient_document_type_id": 1,
       "patient_document_number": "12345678",
       "doctor_document_type_id": 1,
       "doctor_document_number": "87654321",
       "modality": "IN_PERSON",
       "state": "SCHEDULED",
       "notification_state": "PENDING",
       "appointment_type": "CONSULTATION",
       "clinic_id": "CLINIC001",
       "comment": "Consulta de seguimiento",
       "customFields": {
         "room_number": "A-101",
         "specialty": "Cardiología",
         "priority": "Normal",
         "equipment_needed": ["ECG", "Blood pressure monitor"],
         "notes": "Patient prefers morning appointments"
       }
     }'
```

### Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "start_utc": "2024-02-15T10:00:00Z",
  "end_utc": "2024-02-15T11:00:00Z",
  "patient_document_type_id": 1,
  "patient_document_number": "12345678",
  "doctor_document_type_id": 1,
  "doctor_document_number": "87654321",
  "modality": "IN_PERSON",
  "state": "SCHEDULED",
  "notification_state": "PENDING",
  "appointment_type": "CONSULTATION",
  "clinic_id": "CLINIC001",
  "comment": "Consulta de seguimiento",
  "custom_fields": {
    "room_number": "A-101",
    "specialty": "Cardiología",
    "priority": "Normal",
    "equipment_needed": ["ECG", "Blood pressure monitor"],
    "notes": "Patient prefers morning appointments"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 2. Get Appointment

### Request
```bash
curl -X GET "https://api.secre.com/v1/appointments/550e8400-e29b-41d4-a716-446655440000" \
     -H "X-Api-Key: your-api-key-here"
```

### Response
Same as create response above.

## 3. Update Appointment

### Request
```bash
curl -X PATCH "https://api.secre.com/v1/appointments/550e8400-e29b-41d4-a716-446655440000" \
     -H "X-Api-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{
       "eventType": "APPOINTMENT",
       "actionType": "UPDATE",
       "state": "CONFIRMED",
       "notification_state": "SENT",
       "customFields": {
         "room_number": "A-102",
         "specialty": "Cardiología",
         "priority": "High",
         "equipment_needed": ["ECG", "Blood pressure monitor", "Echocardiogram"],
         "notes": "Patient confirmed, prefers morning appointments",
         "insurance_verified": true,
         "copay_amount": 5000
       }
     }'
```

### Response
Updated appointment object with new values.

## 4. Search Appointments

### Search by Patient Document Number
```bash
curl -X GET "https://api.secre.com/v1/appointments/?patient_document_number=12345678" \
     -H "X-Api-Key: your-api-key-here"
```

### Search by Doctor Document Number
```bash
curl -X GET "https://api.secre.com/v1/appointments/?doctor_document_number=87654321" \
     -H "X-Api-Key: your-api-key-here"
```

### Search by State
```bash
curl -X GET "https://api.secre.com/v1/appointments/?state=SCHEDULED" \
     -H "X-Api-Key: your-api-key-here"
```

### Search by Modality
```bash
curl -X GET "https://api.secre.com/v1/appointments/?modality=IN_PERSON" \
     -H "X-Api-Key: your-api-key-here"
```

### Search with Date Range
```bash
curl -X GET "https://api.secre.com/v1/appointments/?start_date=2024-02-01T00:00:00Z&end_date=2024-02-29T23:59:59Z" \
     -H "X-Api-Key: your-api-key-here"
```

### Advanced Search
```bash
curl -X GET "https://api.secre.com/v1/appointments/search?state=CONFIRMED&modality=IN_PERSON&page=1&size=10" \
     -H "X-Api-Key: your-api-key-here"
```

### Date Range Search
```bash
curl -X GET "https://api.secre.com/v1/appointments/by-date-range?start_date=2024-02-01T00:00:00Z&end_date=2024-02-29T23:59:59Z&limit=50" \
     -H "X-Api-Key: your-api-key-here"
```

### Search Response
```json
{
  "appointments": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "tenant_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "start_utc": "2024-02-15T10:00:00Z",
      "end_utc": "2024-02-15T11:00:00Z",
      "patient_document_number": "12345678",
      "doctor_document_number": "87654321",
      "modality": "IN_PERSON",
      "state": "CONFIRMED",
      "custom_fields": {
        "room_number": "A-102",
        "specialty": "Cardiología",
        "priority": "High"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:15:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 50,
  "has_next": false,
  "has_prev": false
}
```

## 5. Delete Appointment

### Request
```bash
curl -X DELETE "https://api.secre.com/v1/appointments/550e8400-e29b-41d4-a716-446655440000" \
     -H "X-Api-Key: your-api-key-here"
```

### Response
```json
{
  "message": "Appointment deleted successfully"
}
```

## Error Responses

### Appointment Not Found (404)
```json
{
  "error": "Appointment not found",
  "detail": "Appointment with ID 550e8400-e29b-41d4-a716-446655440000 not found",
  "trace_id": "req-123456789",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Time Validation Error (400)
```json
{
  "error": "Validation error",
  "detail": "End time must be after start time",
  "trace_id": "req-123456789",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Date Range Error (400)
```json
{
  "error": "Validation error",
  "detail": "End date must be after start date",
  "trace_id": "req-123456789",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Custom Fields Examples

The `customFields` object allows each tenant to store additional appointment data:

### In-Person Appointment
```json
{
  "customFields": {
    "room_number": "A-101",
    "specialty": "Cardiología",
    "priority": "Normal",
    "equipment_needed": ["ECG", "Blood pressure monitor"],
    "notes": "Patient prefers morning appointments",
    "insurance_verified": true,
    "copay_amount": 5000,
    "preparation_instructions": "Fasting required 8 hours before appointment"
  }
}
```

### Virtual Appointment
```json
{
  "customFields": {
    "platform": "Zoom",
    "meeting_link": "https://zoom.us/j/123456789",
    "meeting_id": "123 456 789",
    "passcode": "123456",
    "specialty": "Medicina General",
    "priority": "Normal",
    "preparation_notes": "Patient should have blood work results ready",
    "technical_requirements": "Stable internet connection, camera, microphone"
  }
}
```

### Home Visit Appointment
```json
{
  "customFields": {
    "address": "Calle 123 #45-67, Bogotá",
    "specialty": "Geriatría",
    "priority": "High",
    "equipment_needed": ["Portable ECG", "Blood pressure monitor"],
    "notes": "Elderly patient, mobility issues",
    "contact_person": "María Pérez - +57-300-987-6543",
    "access_instructions": "Ring doorbell twice, apartment 3B",
    "parking_available": true
  }
```

### Emergency Appointment
```json
{
  "customFields": {
    "emergency_type": "Chest pain",
    "priority": "Critical",
    "specialty": "Cardiología",
    "equipment_needed": ["ECG", "Defibrillator", "Oxygen"],
    "notes": "Patient experiencing chest pain, immediate attention required",
    "vital_signs": {
      "blood_pressure": "150/90",
      "heart_rate": "110",
      "temperature": "37.2"
    },
    "allergies": ["Penicilina"],
    "current_medications": ["Aspirin", "Metformin"]
  }
}
```

## Field Validation

### Required Fields
- `startAppointment`: RFC3339 datetime string (start time)
- `endAppointment`: RFC3339 datetime string (end time)
- `patient_document_type_id`: Integer (reference to document type lookup table)
- `patient_document_number`: String, 1-50 characters
- `doctor_document_type_id`: Integer (reference to document type lookup table)
- `doctor_document_number`: String, 1-50 characters
- `modality`: String, 1-50 characters (e.g., "IN_PERSON", "VIRTUAL", "PHONE", "HOME")
- `state`: String, 1-50 characters (e.g., "SCHEDULED", "CONFIRMED", "COMPLETED", "CANCELLED")

### Optional Fields
- `notification_state`: String, max 50 characters
- `appointment_type`: String, max 100 characters
- `clinic_id`: String, max 100 characters
- `comment`: String (unlimited length)
- `custom_fields`: Object (default: {})

### Validation Rules
- `endAppointment` must be after `startAppointment`
- RFC3339 datetime format supports both 'Z' (UTC) and timezone offsets
- All datetime fields are stored as UTC in the database
- Custom fields are stored as JSONB and can contain any valid JSON structure

## Appointment States

Common appointment states:
- `SCHEDULED`: Appointment has been scheduled
- `CONFIRMED`: Patient has confirmed the appointment
- `IN_PROGRESS`: Appointment is currently happening
- `COMPLETED`: Appointment has been completed
- `CANCELLED`: Appointment has been cancelled
- `NO_SHOW`: Patient did not show up
- `RESCHEDULED`: Appointment has been rescheduled

## Appointment Modalities

Common appointment modalities:
- `IN_PERSON`: Traditional in-person appointment
- `VIRTUAL`: Video call appointment
- `PHONE`: Phone call appointment
- `HOME`: Home visit appointment

## Notification States

Common notification states:
- `PENDING`: Notification not yet sent
- `SENT`: Notification has been sent
- `DELIVERED`: Notification has been delivered
- `FAILED`: Notification failed to send
- `BOUNCED`: Notification bounced back
