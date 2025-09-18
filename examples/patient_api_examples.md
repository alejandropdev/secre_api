# Patient API Examples

This document provides comprehensive examples of how to use the Patient CRUD endpoints.

## Authentication

All patient endpoints require API key authentication via the `X-Api-Key` header.

```bash
curl -H "X-Api-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     https://api.secre.com/v1/patients/
```

## 1. Create Patient

### Request
```bash
curl -X POST "https://api.secre.com/v1/patients/" \
     -H "X-Api-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{
       "eventType": "PATIENT",
       "actionType": "CREATE",
       "first_name": "Juan Carlos",
       "first_last_name": "Pérez",
       "second_last_name": "García",
       "birth_date": "1985-05-15",
       "gender_id": 1,
       "document_type_id": 1,
       "document_number": "12345678",
       "email": "juan.perez@example.com",
       "phone": "+57-1-234-5678",
       "cell_phone": "+57-300-123-4567",
       "eps_id": "EPS001",
       "habeas_data": true,
       "customFields": {
         "emergency_contact": "María Pérez - +57-300-987-6543",
         "allergies": ["Penicilina", "Polen"],
         "medical_conditions": ["Hipertensión"],
         "blood_type": "O+",
         "insurance_number": "INS-123456"
       }
     }'
```

### Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "first_name": "Juan Carlos",
  "second_name": null,
  "first_last_name": "Pérez",
  "second_last_name": "García",
  "birth_date": "1985-05-15",
  "gender_id": 1,
  "document_type_id": 1,
  "document_number": "12345678",
  "phone": "+57-1-234-5678",
  "cell_phone": "+57-300-123-4567",
  "email": "juan.perez@example.com",
  "eps_id": "EPS001",
  "habeas_data": true,
  "custom_fields": {
    "emergency_contact": "María Pérez - +57-300-987-6543",
    "allergies": ["Penicilina", "Polen"],
    "medical_conditions": ["Hipertensión"],
    "blood_type": "O+",
    "insurance_number": "INS-123456"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 2. Get Patient

### Request
```bash
curl -X GET "https://api.secre.com/v1/patients/550e8400-e29b-41d4-a716-446655440000" \
     -H "X-Api-Key: your-api-key-here"
```

### Response
Same as create response above.

## 3. Update Patient

### Request
```bash
curl -X PATCH "https://api.secre.com/v1/patients/550e8400-e29b-41d4-a716-446655440000" \
     -H "X-Api-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{
       "eventType": "PATIENT",
       "actionType": "UPDATE",
       "email": "juan.perez.updated@example.com",
       "customFields": {
         "emergency_contact": "María Pérez - +57-300-987-6543",
         "allergies": ["Penicilina", "Polen", "Aspirina"],
         "medical_conditions": ["Hipertensión", "Diabetes"],
         "blood_type": "O+",
         "insurance_number": "INS-123456",
         "preferred_language": "Spanish"
       }
     }'
```

### Response
Updated patient object with new values.

## 4. Search Patients

### Search by Document Number
```bash
curl -X GET "https://api.secre.com/v1/patients/?document_number=12345678" \
     -H "X-Api-Key: your-api-key-here"
```

### Search by Email
```bash
curl -X GET "https://api.secre.com/v1/patients/?email=juan.perez@example.com" \
     -H "X-Api-Key: your-api-key-here"
```

### Search with Pagination
```bash
curl -X GET "https://api.secre.com/v1/patients/?page=1&size=20" \
     -H "X-Api-Key: your-api-key-here"
```

### Advanced Search
```bash
curl -X GET "https://api.secre.com/v1/patients/search?document_type_id=1&email=juan&page=1&size=10" \
     -H "X-Api-Key: your-api-key-here"
```

### Search Response
```json
{
  "patients": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "tenant_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "first_name": "Juan Carlos",
      "first_last_name": "Pérez",
      "document_number": "12345678",
      "email": "juan.perez@example.com",
      "custom_fields": {
        "emergency_contact": "María Pérez - +57-300-987-6543",
        "allergies": ["Penicilina", "Polen"],
        "medical_conditions": ["Hipertensión"]
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 50,
  "has_next": false,
  "has_prev": false
}
```

## 5. Delete Patient

### Request
```bash
curl -X DELETE "https://api.secre.com/v1/patients/550e8400-e29b-41d4-a716-446655440000" \
     -H "X-Api-Key: your-api-key-here"
```

### Response
```json
{
  "message": "Patient deleted successfully"
}
```

## Error Responses

### Patient Not Found (404)
```json
{
  "error": "Patient not found",
  "detail": "Patient with ID 550e8400-e29b-41d4-a716-446655440000 not found",
  "trace_id": "req-123456789",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Validation Error (400)
```json
{
  "error": "Validation error",
  "detail": "Patient with this document already exists",
  "trace_id": "req-123456789",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Unauthorized (401)
```json
{
  "error": "Unauthorized",
  "detail": "API key required. Provide X-Api-Key header.",
  "trace_id": "req-123456789",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Custom Fields Examples

The `customFields` object allows each tenant to store additional patient data without schema changes:

### Medical History
```json
{
  "customFields": {
    "medical_history": {
      "surgeries": ["Appendectomy 2010", "Gallbladder removal 2015"],
      "chronic_conditions": ["Hypertension", "Type 2 Diabetes"],
      "medications": ["Metformin", "Lisinopril"],
      "last_checkup": "2024-01-10"
    }
  }
}
```

### Insurance Information
```json
{
  "customFields": {
    "insurance": {
      "primary_insurer": "EPS Sanitas",
      "policy_number": "POL-123456789",
      "group_number": "GRP-001",
      "coverage_type": "Family",
      "copay_amount": 5000
    }
  }
}
```

### Emergency Contacts
```json
{
  "customFields": {
    "emergency_contacts": [
      {
        "name": "María Pérez",
        "relationship": "Spouse",
        "phone": "+57-300-987-6543",
        "is_primary": true
      },
      {
        "name": "Carlos Pérez",
        "relationship": "Son",
        "phone": "+57-300-555-1234",
        "is_primary": false
      }
    ]
  }
}
```

## Field Validation

### Required Fields
- `first_name`: String, 1-255 characters
- `first_last_name`: String, 1-255 characters
- `birth_date`: Date in YYYY-MM-DD format
- `gender_id`: Integer (reference to gender lookup table)
- `document_type_id`: Integer (reference to document type lookup table)
- `document_number`: String, 1-50 characters

### Optional Fields
- `second_name`: String, max 255 characters
- `second_last_name`: String, max 255 characters
- `phone`: String, max 20 characters
- `cell_phone`: String, max 20 characters
- `email`: String, max 255 characters (must be valid email format)
- `eps_id`: String, max 100 characters
- `habeas_data`: Boolean (default: false)
- `custom_fields`: Object (default: {})

### Validation Rules
- Email must contain '@' symbol
- Phone numbers should contain only digits, '+', '-', and spaces
- Document numbers must be unique within the tenant
- Birth date cannot be in the future
- Custom fields are stored as JSONB and can contain any valid JSON structure
