"""Data normalization service for cleaning and standardizing data."""

import logging
from typing import Any, Dict, List, Optional

from app.utils.validation import DataNormalizer, ValidationError

logger = logging.getLogger(__name__)


class NormalizationService:
    """Service for data normalization and validation."""
    
    def __init__(self):
        self.normalizer = DataNormalizer()
    
    async def normalize_patient_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize patient data before storage."""
        try:
            # Validate data first
            errors = self.normalizer.validate_patient_data(data)
            if errors:
                raise ValidationError(f"Validation errors: {'; '.join(errors)}")
            
            # Normalize data
            normalized_data = self.normalizer.normalize_patient_data(data)
            
            logger.debug(f"Normalized patient data: {len(normalized_data)} fields")
            
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error normalizing patient data: {e}")
            raise ValidationError(f"Failed to normalize patient data: {str(e)}")
    
    async def normalize_appointment_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize appointment data before storage."""
        try:
            # Validate data first
            errors = self.normalizer.validate_appointment_data(data)
            if errors:
                raise ValidationError(f"Validation errors: {'; '.join(errors)}")
            
            # Normalize data
            normalized_data = self.normalizer.normalize_appointment_data(data)
            
            logger.debug(f"Normalized appointment data: {len(normalized_data)} fields")
            
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error normalizing appointment data: {e}")
            raise ValidationError(f"Failed to normalize appointment data: {str(e)}")
    
    async def validate_patient_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate patient data and return list of errors."""
        try:
            errors = self.normalizer.validate_patient_data(data)
            return errors
        except Exception as e:
            logger.error(f"Error validating patient data: {e}")
            return [f"Validation error: {str(e)}"]
    
    async def validate_appointment_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate appointment data and return list of errors."""
        try:
            errors = self.normalizer.validate_appointment_data(data)
            return errors
        except Exception as e:
            logger.error(f"Error validating appointment data: {e}")
            return [f"Validation error: {str(e)}"]
    
    async def normalize_custom_fields(self, custom_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom fields data."""
        try:
            from app.utils.validation import CustomFieldsValidator
            
            if not custom_fields:
                return {}
            
            normalized = CustomFieldsValidator.normalize_custom_fields(custom_fields)
            
            logger.debug(f"Normalized custom fields: {len(normalized)} fields")
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing custom fields: {e}")
            raise ValidationError(f"Failed to normalize custom fields: {str(e)}")
    
    async def validate_custom_fields(self, custom_fields: Dict[str, Any]) -> List[str]:
        """Validate custom fields data."""
        try:
            from app.utils.validation import CustomFieldsValidator
            
            if not custom_fields:
                return []
            
            if not CustomFieldsValidator.validate_custom_fields(custom_fields):
                return ["Invalid custom fields structure"]
            
            return []
            
        except Exception as e:
            logger.error(f"Error validating custom fields: {e}")
            return [f"Custom fields validation error: {str(e)}"]
    
    async def normalize_document_number(self, document_type_id: int, document_number: str) -> str:
        """Normalize document number based on type."""
        try:
            from app.utils.validation import DocumentValidator
            
            normalized = DocumentValidator.normalize_document_number(document_type_id, document_number)
            
            logger.debug(f"Normalized document number: {document_type_id} -> {normalized}")
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing document number: {e}")
            raise ValidationError(f"Failed to normalize document number: {str(e)}")
    
    async def validate_document_number(self, document_type_id: int, document_number: str) -> bool:
        """Validate document number format."""
        try:
            from app.utils.validation import DocumentValidator
            
            is_valid = DocumentValidator.validate_document_number(document_type_id, document_number)
            
            logger.debug(f"Document number validation: {document_type_id} {document_number} -> {is_valid}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating document number: {e}")
            return False
    
    async def normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number."""
        try:
            from app.utils.validation import PhoneValidator
            
            if not phone:
                return phone
            
            normalized = PhoneValidator.normalize_phone(phone)
            
            logger.debug(f"Normalized phone number: {phone} -> {normalized}")
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing phone number: {e}")
            raise ValidationError(f"Failed to normalize phone number: {str(e)}")
    
    async def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format."""
        try:
            from app.utils.validation import PhoneValidator
            
            is_valid = PhoneValidator.validate_phone(phone)
            
            logger.debug(f"Phone number validation: {phone} -> {is_valid}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating phone number: {e}")
            return False
    
    async def normalize_email(self, email: str) -> str:
        """Normalize email address."""
        try:
            from app.utils.validation import EmailValidator
            
            if not email:
                return email
            
            normalized = EmailValidator.normalize_email(email)
            
            logger.debug(f"Normalized email: {email} -> {normalized}")
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing email: {e}")
            raise ValidationError(f"Failed to normalize email: {str(e)}")
    
    async def validate_email(self, email: str) -> bool:
        """Validate email format."""
        try:
            from app.utils.validation import EmailValidator
            
            is_valid = EmailValidator.validate_email(email)
            
            logger.debug(f"Email validation: {email} -> {is_valid}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating email: {e}")
            return False
