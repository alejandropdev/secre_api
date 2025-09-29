"""Patient service for managing patient data."""

import logging
from datetime import date
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundAPIException, ValidationAPIException
from app.models.patient import Patient
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class PatientService:
    """Service for managing patients."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
    
    async def create_patient(
        self,
        tenant_id: UUID,
        first_name: str,
        first_last_name: str,
        birth_date: date,
        gender_id: int,
        document_type_id: int,
        document_number: str,
        second_name: Optional[str] = None,
        second_last_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        eps_id: Optional[str] = None,
        habeas_data: bool = False,
        custom_fields: Optional[Dict[str, Any]] = None,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> Patient:
        """Create a new patient."""
        
        try:
            # Check if patient already exists
            existing_patient = await self.get_patient_by_document(document_type_id, document_number)
            if existing_patient:
                raise ValidationAPIException(
                    f"Patient with document {document_number} already exists",
                    field="document_number"
                )
            
            patient = Patient(
                tenant_id=tenant_id,
                first_name=first_name,
                first_last_name=first_last_name,
                birth_date=birth_date,
                gender_id=gender_id,
                document_type_id=document_type_id,
                document_number=document_number,
                second_name=second_name,
                second_last_name=second_last_name,
                phone=phone,
                email=email,
                eps_id=eps_id,
                habeas_data=habeas_data,
                custom_fields=custom_fields or {},
            )
            
            self.db.add(patient)
            await self.db.commit()
            await self.db.refresh(patient)
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="patient",
                resource_id=patient.id,
                action="create",
                after_snapshot=patient.to_dict() if hasattr(patient, 'to_dict') else None,
                request_context=request_context,
            )
            
            logger.info(f"Created patient {patient.id} for tenant {tenant_id}")
            
            return patient
            
        except ValidationAPIException:
            raise
        except Exception as e:
            logger.error(f"Error creating patient: {e}")
            raise ValidationAPIException(f"Failed to create patient: {str(e)}")
    
    async def get_patient_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """Get patient by ID."""
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()
    
    async def get_patient_by_document(
        self, 
        document_type_id: int, 
        document_number: str
    ) -> Optional[Patient]:
        """Get patient by document type and number."""
        result = await self.db.execute(
            select(Patient).where(
                and_(
                    Patient.document_type_id == document_type_id,
                    Patient.document_number == document_number
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def search_patients(
        self,
        document_type_id: Optional[int] = None,
        document_number: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Patient]:
        """Search patients with filters."""
        
        query = select(Patient)
        conditions = []
        
        if document_type_id:
            conditions.append(Patient.document_type_id == document_type_id)
        if document_number:
            conditions.append(Patient.document_number.ilike(f"%{document_number}%"))
        if email:
            conditions.append(Patient.email.ilike(f"%{email}%"))
        if phone:
            conditions.append(Patient.phone.ilike(f"%{phone}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Patient.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_patient(
        self,
        patient_id: UUID,
        request_context: Optional[Dict[str, Any]] = None,
        **updates: Any,
    ) -> Optional[Patient]:
        """Update patient information."""
        
        try:
            result = await self.db.execute(
                select(Patient).where(Patient.id == patient_id)
            )
            patient = result.scalar_one_or_none()
            
            if not patient:
                raise NotFoundAPIException(f"Patient {patient_id} not found")
            
            # Capture before snapshot
            before_snapshot = patient.to_dict() if hasattr(patient, 'to_dict') else None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(patient, field):
                    setattr(patient, field, value)
            
            await self.db.commit()
            await self.db.refresh(patient)
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="patient",
                resource_id=patient.id,
                action="update",
                before_snapshot=before_snapshot,
                after_snapshot=patient.to_dict() if hasattr(patient, 'to_dict') else None,
                request_context=request_context,
            )
            
            logger.info(f"Updated patient {patient_id}")
            
            return patient
            
        except NotFoundAPIException:
            raise
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {e}")
            raise ValidationAPIException(f"Failed to update patient: {str(e)}")
    
    async def delete_patient(
        self, 
        patient_id: UUID,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Delete a patient."""
        
        try:
            result = await self.db.execute(
                select(Patient).where(Patient.id == patient_id)
            )
            patient = result.scalar_one_or_none()
            
            if not patient:
                raise NotFoundAPIException(f"Patient {patient_id} not found")
            
            # Capture before snapshot
            before_snapshot = patient.to_dict() if hasattr(patient, 'to_dict') else None
            
            await self.db.delete(patient)
            await self.db.commit()
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="patient",
                resource_id=patient_id,
                action="delete",
                before_snapshot=before_snapshot,
                request_context=request_context,
            )
            
            logger.info(f"Deleted patient {patient_id}")
            
            return True
            
        except NotFoundAPIException:
            raise
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {e}")
            raise ValidationAPIException(f"Failed to delete patient: {str(e)}")
