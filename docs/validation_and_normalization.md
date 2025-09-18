# Validation and Normalization Guide

This document describes the comprehensive validation and normalization features implemented in the Secre API.

## Overview

The API includes robust validation and normalization features to ensure data quality, consistency, and compliance with Colombian medical standards. All data is validated at the schema level using Pydantic validators and normalized before storage.

## Validation Features

### 1. Document Number Validation

#### Supported Document Types
- **CC (Cédula de Ciudadanía)**: 6-10 digits
- **CE (Cédula de Extranjería)**: 6-10 digits  
- **TI (Tarjeta de Identidad)**: 6-10 digits
- **RC (Registro Civil)**: 2 letters + 6-10 digits
- **PA (Pasaporte)**: 2 letters + 6-10 digits

#### Validation Rules
```python
# Examples of valid document numbers
"12345678"     # CC - 8 digits
"1234567890"   # CC - 10 digits
"AB12345678"   # RC/PA - 2 letters + 8 digits
"XY123456"     # RC/PA - 2 letters + 6 digits
```

#### Normalization
- Removes spaces and special characters for numeric documents
- Converts to uppercase for alphanumeric documents
- Trims whitespace

### 2. Phone Number Validation

#### Supported Formats
- `+57XXXXXXXXXX` (international format)
- `+57-X-XXX-XXXX` (formatted international)
- `+57 X XXX XXXX` (spaced international)
- `XXXXXXXXXX` (national format)
- `XXX-XXX-XXXX` (formatted national)
- `XXX XXX XXXX` (spaced national)

#### Validation Rules
```python
# Examples of valid phone numbers
"+573001234567"     # International format
"+57-300-123-4567"  # Formatted international
"+57 300 123 4567"  # Spaced international
"3001234567"        # National format
"300-123-4567"      # Formatted national
"300 123 4567"      # Spaced national
```

#### Normalization
- Adds `+57` prefix if missing and number starts with 3
- Removes all non-digit characters except `+`
- Standardizes to `+57XXXXXXXXXX` format

### 3. Email Validation

#### Validation Rules
- Must contain `@` symbol
- Must have valid domain format
- Case insensitive

#### Normalization
- Converts to lowercase
- Trims whitespace

### 4. Date and Time Validation

#### Birth Date Validation
- Cannot be in the future
- Cannot be more than 150 years ago
- Must be valid date format

#### Appointment DateTime Validation
- Start time cannot be in the past (1-hour buffer for timezone issues)
- End time must be after start time
- Appointment cannot be longer than 8 hours
- Supports RFC3339 format with timezone information

#### RFC3339 Format Support
```python
# Supported formats
"2024-02-15T10:00:00Z"           # UTC with Z
"2024-02-15T10:00:00+00:00"      # UTC with offset
"2024-02-15T10:00:00-05:00"      # Timezone offset
```

### 5. Custom Fields Validation

#### Structure Validation
- Maximum 50 custom fields per record
- Maximum 100 characters for field names
- Maximum 1000 characters for field values
- Maximum nesting depth of 3 levels

#### Allowed Data Types
- Strings
- Numbers
- Booleans
- Arrays
- Nested objects (up to 3 levels deep)

#### Example Valid Custom Fields
```json
{
  "emergency_contact": "María Pérez - +57-300-987-6543",
  "allergies": ["Penicilina", "Polen"],
  "medical_conditions": ["Hipertensión", "Diabetes"],
  "insurance": {
    "provider": "EPS Sanitas",
    "policy_number": "POL-123456789",
    "coverage_type": "Family"
  },
  "vital_signs": {
    "blood_pressure": "120/80",
    "heart_rate": 72,
    "temperature": 36.5
  }
}
```

## Error Handling

### Validation Error Responses

When validation fails, the API returns detailed error information:

```json
{
  "detail": [
    {
      "loc": ["body", "document_number"],
      "msg": "Invalid document number format for type 1",
      "type": "value_error"
    },
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

### Common Validation Errors

#### Document Number Errors
- `"Invalid document number format for type {type_id}"`
- `"Invalid document type ID: {type_id}"`

#### Phone Number Errors
- `"Invalid phone number format"`

#### Email Errors
- `"Invalid email format"`

#### Date/Time Errors
- `"Birth date cannot be in the future"`
- `"Birth date is too old (more than 150 years)"`
- `"Appointment start time cannot be in the past"`
- `"Appointment end time must be after start time"`
- `"Appointment cannot be longer than 8 hours"`
- `"Invalid RFC3339 datetime format"`

#### Custom Fields Errors
- `"Too many custom fields (max 50)"`
- `"Invalid custom field name: {field_name}"`
- `"Custom field value too long: {field_name}"`
- `"Custom fields nested too deeply (max depth 3)"`

## Normalization Examples

### Patient Data Normalization

#### Input Data
```json
{
  "first_name": "Juan Carlos",
  "last_name": "Pérez García",
  "document_type_id": 1,
  "document_number": " 12 34 56 78 ",
  "phone": "300 123 4567",
  "cell_phone": "+57-300-555-1234",
  "email": "JUAN.PEREZ@EXAMPLE.COM",
  "custom_fields": {
    "emergency_contact": "  María Pérez  ",
    "allergies": ["Penicilina", "Polen"]
  }
}
```

#### Normalized Output
```json
{
  "first_name": "Juan Carlos",
  "last_name": "Pérez García",
  "document_type_id": 1,
  "document_number": "12345678",
  "phone": "+573001234567",
  "cell_phone": "+573005551234",
  "email": "juan.perez@example.com",
  "custom_fields": {
    "emergency_contact": "María Pérez",
    "allergies": ["Penicilina", "Polen"]
  }
}
```

### Appointment Data Normalization

#### Input Data
```json
{
  "startAppointment": "2024-02-15T10:00:00Z",
  "endAppointment": "2024-02-15T11:00:00+00:00",
  "custom_fields": {
    "room_number": "  A-101  ",
    "specialty": "Cardiología",
    "equipment_needed": ["ECG", "Blood pressure monitor"]
  }
}
```

#### Normalized Output
```json
{
  "start_utc": "2024-02-15T10:00:00",
  "end_utc": "2024-02-15T11:00:00",
  "custom_fields": {
    "room_number": "A-101",
    "specialty": "Cardiología",
    "equipment_needed": ["ECG", "Blood pressure monitor"]
  }
}
```

## Testing Validation

### Running Validation Tests

```bash
# Run the validation test script
python scripts/test_validation.py
```

### Test Coverage

The validation test script covers:

1. **Valid Data**: Tests that properly formatted data is accepted
2. **Invalid Document Numbers**: Tests various invalid document formats
3. **Invalid Email Addresses**: Tests malformed email addresses
4. **Invalid Phone Numbers**: Tests various invalid phone formats
5. **Invalid Dates**: Tests future birth dates and invalid appointment times
6. **Custom Fields Validation**: Tests field limits and structure
7. **Normalization**: Tests that data is properly normalized

### Manual Testing

You can test validation manually using the API endpoints:

```bash
# Test valid patient creation
curl -X POST "http://localhost:8000/v1/patients/" \
     -H "X-Api-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "eventType": "PATIENT",
       "actionType": "CREATE",
       "first_name": "Test",
       "first_last_name": "User",
       "birth_date": "1990-01-01",
       "gender_id": 1,
       "document_type_id": 1,
       "document_number": "12345678",
       "email": "test@example.com",
       "phone": "300-123-4567"
     }'

# Test invalid data (should return 422)
curl -X POST "http://localhost:8000/v1/patients/" \
     -H "X-Api-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "eventType": "PATIENT",
       "actionType": "CREATE",
       "first_name": "Test",
       "first_last_name": "User",
       "birth_date": "1990-01-01",
       "gender_id": 1,
       "document_type_id": 1,
       "document_number": "invalid-doc",
       "email": "invalid-email"
     }'
```

## Best Practices

### For API Consumers

1. **Always validate data client-side** before sending to the API
2. **Handle validation errors gracefully** and provide user feedback
3. **Use the correct document type IDs** as specified in the lookup endpoints
4. **Format phone numbers consistently** using Colombian standards
5. **Use RFC3339 format** for datetime fields
6. **Keep custom fields simple** and avoid deep nesting

### For API Developers

1. **Always use the validation service** for data normalization
2. **Test edge cases** thoroughly with the validation test script
3. **Monitor validation errors** in logs for data quality insights
4. **Update validation rules** as business requirements change
5. **Document new validation rules** in this guide

## Configuration

### Validation Limits

The following limits can be configured in the validation service:

```python
# Custom fields limits
MAX_CUSTOM_FIELDS = 50
MAX_FIELD_NAME_LENGTH = 100
MAX_FIELD_VALUE_LENGTH = 1000
MAX_NESTING_DEPTH = 3

# Date validation limits
MAX_AGE_YEARS = 150
MAX_APPOINTMENT_HOURS = 8
TIMEZONE_BUFFER_HOURS = 1
```

### Adding New Validation Rules

To add new validation rules:

1. Create a new validator class in `app/utils/validation.py`
2. Add the validator to `app/schemas/validators.py`
3. Update the Pydantic schemas to use the new validator
4. Add tests to the validation test script
5. Update this documentation

## Troubleshooting

### Common Issues

1. **Document number validation failing**: Check that the document type ID is correct and the number matches the expected format
2. **Phone number normalization issues**: Ensure the number follows Colombian phone number patterns
3. **Email validation failing**: Check for proper email format with @ symbol and valid domain
4. **Custom fields validation errors**: Verify field count, name length, and nesting depth limits
5. **DateTime validation issues**: Ensure RFC3339 format and reasonable time constraints

### Debug Mode

Enable debug logging to see validation details:

```python
# In app/core/config.py
LOG_LEVEL = "DEBUG"
```

This will log detailed information about validation and normalization processes.
