"""Enhanced Pydantic validators with custom validation logic."""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, validator


class DocumentNumberValidator:
    """Validator for document numbers based on Colombian standards."""
    
    DOCUMENT_PATTERNS = {
        1: r'^\d{6,10}$',  # CC - Cédula de Ciudadanía
        2: r'^\d{6,10}$',  # CE - Cédula de Extranjería
        3: r'^\d{6,10}$',  # TI - Tarjeta de Identidad
        4: r'^[A-Z]{2}\d{6,10}$',  # RC - Registro Civil
        5: r'^[A-Z]{2}\d{6,10}$',  # PA - Pasaporte
    }
    
    @classmethod
    def validate_document(cls, document_type_id: int, document_number: str) -> str:
        """Validate and normalize document number."""
        if document_type_id not in cls.DOCUMENT_PATTERNS:
            raise ValueError(f"Invalid document type ID: {document_type_id}")
        
        # Normalize document number
        normalized = document_number.strip().upper()
        
        # Remove spaces and special characters for numeric documents
        if document_type_id in [1, 2, 3]:
            normalized = re.sub(r'[^\d]', '', normalized)
        
        # Validate format
        pattern = cls.DOCUMENT_PATTERNS[document_type_id]
        if not re.match(pattern, normalized):
            raise ValueError(f"Invalid document number format for type {document_type_id}")
        
        return normalized


class PhoneNumberValidator:
    """Validator for phone numbers with Colombian standards."""
    
    PHONE_PATTERNS = [
        r'^\+57\d{10}$',  # +57XXXXXXXXXX
        r'^\+57-\d{1,3}-\d{3}-\d{4}$',  # +57-X-XXX-XXXX
        r'^\+57\s\d{1,3}\s\d{3}\s\d{4}$',  # +57 X XXX XXXX
        r'^\d{10}$',  # XXXXXXXXXX
        r'^\d{3}-\d{3}-\d{4}$',  # XXX-XXX-XXXX
        r'^\d{3}\s\d{3}\s\d{4}$',  # XXX XXX XXXX
    ]
    
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Validate and normalize phone number."""
        if not phone:
            return phone
        
        # Remove all non-digit characters except +
        normalized = re.sub(r'[^\d+]', '', phone.strip())
        
        # Add +57 if not present and starts with 3
        if normalized.startswith('3') and len(normalized) == 10:
            normalized = '+57' + normalized
        elif normalized.startswith('57') and len(normalized) == 12:
            normalized = '+' + normalized
        elif not normalized.startswith('+57') and len(normalized) == 10:
            normalized = '+57' + normalized
        
        # Validate final format
        if not any(re.match(pattern, normalized) for pattern in cls.PHONE_PATTERNS):
            raise ValueError("Invalid phone number format")
        
        return normalized


class EmailValidator:
    """Validator for email addresses."""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate and normalize email address."""
        if not email:
            return email
        
        normalized = email.strip().lower()
        
        if not re.match(cls.EMAIL_PATTERN, normalized):
            raise ValueError("Invalid email format")
        
        return normalized


class DateTimeValidator:
    """Validator for datetime fields with UTC normalization."""
    
    @classmethod
    def validate_rfc3339_datetime(cls, dt: str) -> datetime:
        """Validate and normalize RFC3339 datetime to UTC."""
        try:
            # Handle RFC3339 format
            if dt.endswith('Z'):
                dt = dt[:-1] + '+00:00'
            
            parsed_dt = datetime.fromisoformat(dt)
            
            # Convert to UTC if timezone aware
            if parsed_dt.tzinfo is not None:
                parsed_dt = parsed_dt.astimezone().replace(tzinfo=None)
            
            return parsed_dt
            
        except ValueError as e:
            raise ValueError(f"Invalid RFC3339 datetime format: {e}")
    
    @classmethod
    def validate_birth_date(cls, birth_date: date) -> date:
        """Validate birth date is reasonable."""
        today = date.today()
        
        # Birth date cannot be in the future
        if birth_date > today:
            raise ValueError("Birth date cannot be in the future")
        
        # Birth date cannot be more than 150 years ago
        min_date = date(today.year - 150, today.month, today.day)
        if birth_date < min_date:
            raise ValueError("Birth date is too old (more than 150 years)")
        
        return birth_date
    
    @classmethod
    def validate_appointment_datetime(cls, start_utc: datetime, end_utc: datetime) -> tuple[datetime, datetime]:
        """Validate appointment datetime constraints."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        
        # Start time cannot be in the past (allow 1 hour buffer for timezone issues)
        if start_utc < now - timedelta(hours=1):
            raise ValueError("Appointment start time cannot be in the past")
        
        # End time must be after start time
        if end_utc <= start_utc:
            raise ValueError("Appointment end time must be after start time")
        
        # Appointment cannot be longer than 8 hours
        if (end_utc - start_utc).total_seconds() > 8 * 3600:
            raise ValueError("Appointment cannot be longer than 8 hours")
        
        return start_utc, end_utc


class CustomFieldsValidator:
    """Validator for custom fields JSONB data."""
    
    MAX_CUSTOM_FIELDS = 50
    MAX_FIELD_NAME_LENGTH = 100
    MAX_FIELD_VALUE_LENGTH = 1000
    
    @classmethod
    def validate_custom_fields(cls, custom_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize custom fields."""
        if not isinstance(custom_fields, dict):
            raise ValueError("Custom fields must be a dictionary")
        
        # Check maximum number of fields
        if len(custom_fields) > cls.MAX_CUSTOM_FIELDS:
            raise ValueError(f"Too many custom fields (max {cls.MAX_CUSTOM_FIELDS})")
        
        normalized = {}
        for key, value in custom_fields.items():
            # Validate field name
            if not isinstance(key, str) or len(key) > cls.MAX_FIELD_NAME_LENGTH:
                raise ValueError(f"Invalid custom field name: {key}")
            
            # Normalize key
            normalized_key = key.strip()[:cls.MAX_FIELD_NAME_LENGTH]
            
            # Validate and normalize field value
            if isinstance(value, str):
                if len(value) > cls.MAX_FIELD_VALUE_LENGTH:
                    raise ValueError(f"Custom field value too long: {key}")
                normalized_value = value.strip()[:cls.MAX_FIELD_VALUE_LENGTH]
            elif isinstance(value, dict):
                normalized_value = cls._validate_nested_dict(value, depth=0)
            else:
                normalized_value = value
            
            normalized[normalized_key] = normalized_value
        
        return normalized
    
    @classmethod
    def _validate_nested_dict(cls, data: Dict[str, Any], depth: int) -> Dict[str, Any]:
        """Validate nested dictionary structure (max depth 3)."""
        if depth > 3:
            raise ValueError("Custom fields nested too deeply (max depth 3)")
        
        normalized = {}
        for key, value in data.items():
            if not isinstance(key, str) or len(key) > cls.MAX_FIELD_NAME_LENGTH:
                raise ValueError(f"Invalid nested field name: {key}")
            
            normalized_key = key.strip()[:cls.MAX_FIELD_NAME_LENGTH]
            
            if isinstance(value, str):
                if len(value) > cls.MAX_FIELD_VALUE_LENGTH:
                    raise ValueError(f"Nested field value too long: {key}")
                normalized_value = value.strip()[:cls.MAX_FIELD_VALUE_LENGTH]
            elif isinstance(value, dict):
                normalized_value = cls._validate_nested_dict(value, depth + 1)
            else:
                normalized_value = value
            
            normalized[normalized_key] = normalized_value
        
        return normalized


class EnhancedValidators:
    """Collection of enhanced validators for Pydantic models."""
    
    @staticmethod
    def validate_document_number(cls, v, values):
        """Validate document number based on document type."""
        if 'document_type_id' in values:
            return DocumentNumberValidator.validate_document(values['document_type_id'], v)
        return v
    
    @staticmethod
    def validate_phone(cls, v):
        """Validate phone number."""
        return PhoneNumberValidator.validate_phone(v)
    
    @staticmethod
    def validate_cell_phone(cls, v):
        """Validate cell phone number."""
        return PhoneNumberValidator.validate_phone(v)
    
    @staticmethod
    def validate_email(cls, v):
        """Validate email address."""
        return EmailValidator.validate_email(v)
    
    @staticmethod
    def validate_birth_date(cls, v):
        """Validate birth date."""
        return DateTimeValidator.validate_birth_date(v)
    
    @staticmethod
    def validate_rfc3339_datetime(cls, v):
        """Validate RFC3339 datetime."""
        return DateTimeValidator.validate_rfc3339_datetime(v)
    
    @staticmethod
    def validate_appointment_datetime(cls, v, values):
        """Validate appointment datetime constraints."""
        if 'start_utc' in values and 'end_utc' in values:
            return DateTimeValidator.validate_appointment_datetime(values['start_utc'], v)[1]
        return v
    
    @staticmethod
    def validate_custom_fields(cls, v):
        """Validate custom fields."""
        return CustomFieldsValidator.validate_custom_fields(v)
