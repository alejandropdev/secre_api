"""Appointment service for managing appointment data."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundAPIException, ValidationAPIException
from app.models.appointment import Appointment
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class AppointmentService:
    """Service for managing appointments."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
    
    async def create_appointment(
        self,
        tenant_id: UUID,
        start_utc: datetime,
        end_utc: datetime,
        patient_document_type_id: int,
        patient_document_number: str,
        doctor_document_type_id: int,
        doctor_document_number: str,
        modality_id: int,
        state_id: int,
        notification_state: Optional[str] = None,
        appointment_type_id: Optional[int] = None,
        clinic_id: Optional[int] = None,
        comment: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> Appointment:
        """Create a new appointment."""
        
        try:
            # Validate appointment times
            if end_utc <= start_utc:
                raise ValidationAPIException(
                    "End time must be after start time",
                    field="end_utc"
                )
            
            appointment = Appointment(
                tenant_id=tenant_id,
                start_utc=start_utc,
                end_utc=end_utc,
                patient_document_type_id=patient_document_type_id,
                patient_document_number=patient_document_number,
                doctor_document_type_id=doctor_document_type_id,
                doctor_document_number=doctor_document_number,
                modality_id=modality_id,
                state_id=state_id,
                notification_state=notification_state,
                appointment_type_id=appointment_type_id,
                clinic_id=clinic_id,
                comment=comment,
                custom_fields=custom_fields or {},
            )
            
            self.db.add(appointment)
            await self.db.commit()
            await self.db.refresh(appointment)
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="appointment",
                resource_id=appointment.id,
                action="create",
                after_snapshot=appointment.to_dict() if hasattr(appointment, 'to_dict') else None,
                request_context=request_context,
            )
            
            logger.info(f"Created appointment {appointment.id} for tenant {tenant_id}")
            
            return appointment
            
        except ValidationAPIException:
            raise
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            raise ValidationAPIException(f"Failed to create appointment: {str(e)}")
    
    async def get_appointment_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        """Get appointment by ID."""
        result = await self.db.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.modality),
                selectinload(Appointment.state),
                selectinload(Appointment.appointment_type),
                selectinload(Appointment.clinic)
            )
            .where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()
    
    async def search_appointments(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        modality_id: Optional[int] = None,
        state_id: Optional[int] = None,
        patient_document_number: Optional[str] = None,
        doctor_document_number: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Appointment]:
        """Search appointments with filters."""
        
        query = select(Appointment).options(
            selectinload(Appointment.modality),
            selectinload(Appointment.state),
            selectinload(Appointment.appointment_type),
            selectinload(Appointment.clinic)
        )
        conditions = []
        
        if start_date:
            conditions.append(Appointment.start_utc >= start_date)
        if end_date:
            conditions.append(Appointment.end_utc <= end_date)
        if modality_id:
            conditions.append(Appointment.modality_id == modality_id)
        if state_id:
            conditions.append(Appointment.state_id == state_id)
        if patient_document_number:
            conditions.append(Appointment.patient_document_number == patient_document_number)
        if doctor_document_number:
            conditions.append(Appointment.doctor_document_number == doctor_document_number)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Appointment.start_utc.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_appointment(
        self,
        appointment_id: UUID,
        request_context: Optional[Dict[str, Any]] = None,
        **updates: Any,
    ) -> Optional[Appointment]:
        """Update appointment information."""
        
        try:
            result = await self.db.execute(
                select(Appointment).where(Appointment.id == appointment_id)
            )
            appointment = result.scalar_one_or_none()
            
            if not appointment:
                raise NotFoundAPIException(f"Appointment {appointment_id} not found")
            
            # Capture before snapshot
            before_snapshot = appointment.to_dict() if hasattr(appointment, 'to_dict') else None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(appointment, field):
                    setattr(appointment, field, value)
            
            # Validate updated times if they were changed
            if 'start_utc' in updates or 'end_utc' in updates:
                if appointment.end_utc <= appointment.start_utc:
                    raise ValidationAPIException(
                        "End time must be after start time",
                        field="end_utc"
                    )
            
            await self.db.commit()
            await self.db.refresh(appointment)
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="appointment",
                resource_id=appointment.id,
                action="update",
                before_snapshot=before_snapshot,
                after_snapshot=appointment.to_dict() if hasattr(appointment, 'to_dict') else None,
                request_context=request_context,
            )
            
            # Reload appointment with eager loaded relations to avoid lazy loading issues
            stmt = select(Appointment).options(
                selectinload(Appointment.modality),
                selectinload(Appointment.state),
                selectinload(Appointment.appointment_type),
                selectinload(Appointment.clinic)
            ).where(Appointment.id == appointment_id)
            
            result = await self.db.execute(stmt)
            appointment_with_relations = result.scalar_one()
            
            logger.info(f"Updated appointment {appointment_id}")
            
            return appointment_with_relations
            
        except NotFoundAPIException:
            raise
        except ValidationAPIException:
            raise
        except Exception as e:
            logger.error(f"Error updating appointment {appointment_id}: {e}")
            raise ValidationAPIException(f"Failed to update appointment: {str(e)}")
    
    async def delete_appointment(
        self, 
        appointment_id: UUID,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Delete an appointment."""
        
        try:
            result = await self.db.execute(
                select(Appointment).where(Appointment.id == appointment_id)
            )
            appointment = result.scalar_one_or_none()
            
            if not appointment:
                raise NotFoundAPIException(f"Appointment {appointment_id} not found")
            
            # Capture before snapshot
            before_snapshot = appointment.to_dict() if hasattr(appointment, 'to_dict') else None
            
            await self.db.delete(appointment)
            await self.db.commit()
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="appointment",
                resource_id=appointment_id,
                action="delete",
                before_snapshot=before_snapshot,
                request_context=request_context,
            )
            
            logger.info(f"Deleted appointment {appointment_id}")
            
            return True
            
        except NotFoundAPIException:
            raise
        except Exception as e:
            logger.error(f"Error deleting appointment {appointment_id}: {e}")
            raise ValidationAPIException(f"Failed to delete appointment: {str(e)}")
    
    async def get_appointments_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Appointment]:
        """Get appointments within a date range."""
        
        query = select(Appointment).options(
            selectinload(Appointment.modality),
            selectinload(Appointment.state),
            selectinload(Appointment.appointment_type),
            selectinload(Appointment.clinic)
        ).where(
            and_(
                Appointment.start_utc >= start_date,
                Appointment.end_utc <= end_date
            )
        ).order_by(Appointment.start_utc).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
