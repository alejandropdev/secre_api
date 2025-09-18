"""Validation utilities for data validation and normalization."""

import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union


class ValidationError(Exception):
    """Custom validation error with detailed field information."""
    
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)


class DocumentValidator:
    """Validator for document numbers based on type."""
    
    # Colombian document patterns
    DOCUMENT_PATTERNS = {
        1: r'^\d{6,10}$',  # CC - Cédula de Ciudadanía
        2: r'^\d{6,10}$',  # CE - Cédula de Extranjería
        3: r'^\d{6,10}$',  # TI - Tarjeta de Identidad
        4: r'^[A-Z]{2}\d{6,10}$',  # RC - Registro Civil
        5: r'^[A-Z]{2}\d{6,10}$',  # PA - Pasaporte
    }
    
    @classmethod
    def validate_document_number(cls, document_type_id: int, document_number: str) -> bool:
        """Validate document number based on type."""
        if document_type_id not in cls.DOCUMENT_PATTERNS:
            return False
        
        pattern = cls.DOCUMENT_PATTERNS[document_type_id]
        return bool(re.match(pattern, document_number.strip()))
    
    @classmethod
    def normalize_document_number(cls, document_type_id: int, document_number: str) -> str:
        """Normalize document number by removing spaces and converting to uppercase."""
        normalized = document_number.strip().upper()
        
        # Remove any spaces or special characters for numeric documents
        if document_type_id in [1, 2, 3]:
            normalized = re.sub(r'[^\d]', '', normalized)
        
        return normalized


class PhoneValidator:
    """Validator for phone numbers."""
    
    # Colombian phone patterns
    PHONE_PATTERNS = [
        r'^\+57\d{10}$',  # +57XXXXXXXXXX
        r'^\+57-\d{1,3}-\d{3}-\d{4}$',  # +57-X-XXX-XXXX
        r'^\+57\s\d{1,3}\s\d{3}\s\d{4}$',  # +57 X XXX XXXX
        r'^\d{10}$',  # XXXXXXXXXX
        r'^\d{3}-\d{3}-\d{4}$',  # XXX-XXX-XXXX
        r'^\d{3}\s\d{3}\s\d{4}$',  # XXX XXX XXXX
    ]
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return True  # Optional field
        
        phone = phone.strip()
        return any(re.match(pattern, phone) for pattern in cls.PHONE_PATTERNS)
    
    @classmethod
    def normalize_phone(cls, phone: str) -> str:
        """Normalize phone number to standard format."""
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
        
        return normalized


class EmailValidator:
    """Validator for email addresses."""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format."""
        if not email:
            return True  # Optional field
        
        return bool(re.match(cls.EMAIL_PATTERN, email.strip().lower()))
    
    @classmethod
    def normalize_email(cls, email: str) -> str:
        """Normalize email address."""
        if not email:
            return email
        
        return email.strip().lower()


class DateValidator:
    """Validator for dates and datetimes."""
    
    @classmethod
    def validate_birth_date(cls, birth_date: date) -> bool:
        """Validate birth date is reasonable."""
        today = date.today()
        
        # Birth date cannot be in the future
        if birth_date > today:
            return False
        
        # Birth date cannot be more than 150 years ago
        min_date = date(today.year - 150, today.month, today.day)
        if birth_date < min_date:
            return False
        
        return True
    
    @classmethod
    def validate_appointment_datetime(cls, start_utc: datetime, end_utc: datetime) -> bool:
        """Validate appointment datetime constraints."""
        now = datetime.utcnow()
        
        # Start time cannot be in the past (allow 1 hour buffer for timezone issues)
        if start_utc < now - timedelta(hours=1):
            return False
        
        # End time must be after start time
        if end_utc <= start_utc:
            return False
        
        # Appointment cannot be longer than 8 hours
        if (end_utc - start_utc).total_seconds() > 8 * 3600:
            return False
        
        return True
    
    @classmethod
    def normalize_datetime_to_utc(cls, dt: Union[str, datetime]) -> datetime:
        """Normalize datetime to UTC."""
        if isinstance(dt, str):
            # Handle RFC3339 format
            if dt.endswith('Z'):
                dt = dt[:-1] + '+00:00'
            dt = datetime.fromisoformat(dt)
        
        # Convert to UTC if timezone aware
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        
        return dt


class CustomFieldsValidator:
    """Validator for custom fields JSONB data."""
    
    MAX_CUSTOM_FIELDS = 50
    MAX_FIELD_NAME_LENGTH = 100
    MAX_FIELD_VALUE_LENGTH = 1000
    
    @classmethod
    def validate_custom_fields(cls, custom_fields: Dict[str, Any]) -> bool:
        """Validate custom fields structure and content."""
        if not isinstance(custom_fields, dict):
            return False
        
        # Check maximum number of fields
        if len(custom_fields) > cls.MAX_CUSTOM_FIELDS:
            return False
        
        for key, value in custom_fields.items():
            # Validate field name
            if not isinstance(key, str) or len(key) > cls.MAX_FIELD_NAME_LENGTH:
                return False
            
            # Validate field value
            if isinstance(value, str) and len(value) > cls.MAX_FIELD_VALUE_LENGTH:
                return False
            
            # Validate nested structures
            if isinstance(value, dict) and not cls._validate_nested_dict(value, depth=0):
                return False
        
        return True
    
    @classmethod
    def _validate_nested_dict(cls, data: Dict[str, Any], depth: int) -> bool:
        """Validate nested dictionary structure (max depth 3)."""
        if depth > 3:
            return False
        
        for key, value in data.items():
            if not isinstance(key, str) or len(key) > cls.MAX_FIELD_NAME_LENGTH:
                return False
            
            if isinstance(value, str) and len(value) > cls.MAX_FIELD_VALUE_LENGTH:
                return False
            
            if isinstance(value, dict) and not cls._validate_nested_dict(value, depth + 1):
                return False
        
        return True
    
    @classmethod
    def normalize_custom_fields(cls, custom_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom fields by cleaning and validating."""
        if not custom_fields:
            return {}
        
        normalized = {}
        for key, value in custom_fields.items():
            # Normalize key
            normalized_key = key.strip()[:cls.MAX_FIELD_NAME_LENGTH]
            
            # Normalize value based on type
            if isinstance(value, str):
                normalized_value = value.strip()[:cls.MAX_FIELD_VALUE_LENGTH]
            elif isinstance(value, dict):
                normalized_value = cls._normalize_nested_dict(value, depth=0)
            else:
                normalized_value = value
            
            normalized[normalized_key] = normalized_value
        
        return normalized
    
    @classmethod
    def _normalize_nested_dict(cls, data: Dict[str, Any], depth: int) -> Dict[str, Any]:
        """Normalize nested dictionary structure."""
        if depth > 3:
            return {}
        
        normalized = {}
        for key, value in data.items():
            normalized_key = key.strip()[:cls.MAX_FIELD_NAME_LENGTH]
            
            if isinstance(value, str):
                normalized_value = value.strip()[:cls.MAX_FIELD_VALUE_LENGTH]
            elif isinstance(value, dict):
                normalized_value = cls._normalize_nested_dict(value, depth + 1)
            else:
                normalized_value = value
            
            normalized[normalized_key] = normalized_value
        
        return normalized


class DataNormalizer:
    """Main data normalizer that coordinates all validation and normalization."""
    
    @classmethod
    def normalize_patient_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize patient data."""
        normalized = data.copy()
        
        # Normalize document number
        if 'document_number' in normalized and 'document_type_id' in normalized:
            normalized['document_number'] = DocumentValidator.normalize_document_number(
                normalized['document_type_id'],
                normalized['document_number']
            )
        
        # Normalize phone numbers
        if 'phone' in normalized:
            normalized['phone'] = PhoneValidator.normalize_phone(normalized['phone'])
        
        if 'cell_phone' in normalized:
            normalized['cell_phone'] = PhoneValidator.normalize_phone(normalized['cell_phone'])
        
        # Normalize email
        if 'email' in normalized:
            normalized['email'] = EmailValidator.normalize_email(normalized['email'])
        
        # Normalize custom fields
        if 'custom_fields' in normalized:
            normalized['custom_fields'] = CustomFieldsValidator.normalize_custom_fields(
                normalized['custom_fields']
            )
        
        return normalized
    
    @classmethod
    def normalize_appointment_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize appointment data."""
        normalized = data.copy()
        
        # Normalize datetime fields
        if 'start_utc' in normalized:
            normalized['start_utc'] = DateValidator.normalize_datetime_to_utc(normalized['start_utc'])
        
        if 'end_utc' in normalized:
            normalized['end_utc'] = DateValidator.normalize_datetime_to_utc(normalized['end_utc'])
        
        # Normalize custom fields
        if 'custom_fields' in normalized:
            normalized['custom_fields'] = CustomFieldsValidator.normalize_custom_fields(
                normalized['custom_fields']
            )
        
        return normalized
    
    @classmethod
    def validate_patient_data(cls, data: Dict[str, Any]) -> List[str]:
        """Validate patient data and return list of errors."""
        errors = []
        
        # Validate document number
        if 'document_number' in data and 'document_type_id' in data:
            if not DocumentValidator.validate_document_number(
                data['document_type_id'], data['document_number']
            ):
                errors.append(f"Invalid document number format for type {data['document_type_id']}")
        
        # Validate phone numbers
        if 'phone' in data and not PhoneValidator.validate_phone(data['phone']):
            errors.append("Invalid phone number format")
        
        if 'cell_phone' in data and not PhoneValidator.validate_phone(data['cell_phone']):
            errors.append("Invalid cell phone number format")
        
        # Validate email
        if 'email' in data and not EmailValidator.validate_email(data['email']):
            errors.append("Invalid email format")
        
        # Validate birth date
        if 'birth_date' in data:
            if isinstance(data['birth_date'], str):
                try:
                    birth_date = datetime.fromisoformat(data['birth_date']).date()
                except ValueError:
                    errors.append("Invalid birth date format")
                else:
                    if not DateValidator.validate_birth_date(birth_date):
                        errors.append("Invalid birth date (future date or too old)")
            elif isinstance(data['birth_date'], date):
                if not DateValidator.validate_birth_date(data['birth_date']):
                    errors.append("Invalid birth date (future date or too old)")
        
        # Validate custom fields
        if 'custom_fields' in data:
            if not CustomFieldsValidator.validate_custom_fields(data['custom_fields']):
                errors.append("Invalid custom fields structure")
        
        return errors
    
    @classmethod
    def validate_appointment_data(cls, data: Dict[str, Any]) -> List[str]:
        """Validate appointment data and return list of errors."""
        errors = []
        
        # Validate datetime fields
        if 'start_utc' in data and 'end_utc' in data:
            try:
                start_utc = DateValidator.normalize_datetime_to_utc(data['start_utc'])
                end_utc = DateValidator.normalize_datetime_to_utc(data['end_utc'])
                
                if not DateValidator.validate_appointment_datetime(start_utc, end_utc):
                    errors.append("Invalid appointment datetime (past date, end before start, or too long)")
            except (ValueError, TypeError):
                errors.append("Invalid datetime format")
        
        # Validate custom fields
        if 'custom_fields' in data:
            if not CustomFieldsValidator.validate_custom_fields(data['custom_fields']):
                errors.append("Invalid custom fields structure")
        
        return errors
