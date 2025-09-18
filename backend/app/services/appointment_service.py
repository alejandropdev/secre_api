"""Appointment service for managing appointment data."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment

logger = logging.getLogger(__name__)


class AppointmentService:
    """Service for managing appointments."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_appointment(
        self,
        tenant_id: UUID,
        start_utc: datetime,
        end_utc: datetime,
        patient_document_type_id: int,
        patient_document_number: str,
        doctor_document_type_id: int,
        doctor_document_number: str,
        modality: str,
        state: str,
        notification_state: Optional[str] = None,
        appointment_type: Optional[str] = None,
        clinic_id: Optional[str] = None,
        comment: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> Appointment:
        """Create a new appointment."""
        
        appointment = Appointment(
            tenant_id=tenant_id,
            start_utc=start_utc,
            end_utc=end_utc,
            patient_document_type_id=patient_document_type_id,
            patient_document_number=patient_document_number,
            doctor_document_type_id=doctor_document_type_id,
            doctor_document_number=doctor_document_number,
            modality=modality,
            state=state,
            notification_state=notification_state,
            appointment_type=appointment_type,
            clinic_id=clinic_id,
            comment=comment,
            custom_fields=custom_fields or {},
        )
        
        self.db.add(appointment)
        await self.db.commit()
        await self.db.refresh(appointment)
        
        logger.info(f"Created appointment {appointment.id} for tenant {tenant_id}")
        
        return appointment
    
    async def get_appointment_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        """Get appointment by ID."""
        result = await self.db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()
    
    async def search_appointments(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        modality: Optional[str] = None,
        state: Optional[str] = None,
        patient_document_number: Optional[str] = None,
        doctor_document_number: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Appointment]:
        """Search appointments with filters."""
        
        query = select(Appointment)
        conditions = []
        
        if start_date:
            conditions.append(Appointment.start_utc >= start_date)
        if end_date:
            conditions.append(Appointment.end_utc <= end_date)
        if modality:
            conditions.append(Appointment.modality == modality)
        if state:
            conditions.append(Appointment.state == state)
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
        **updates: Any,
    ) -> Optional[Appointment]:
        """Update appointment information."""
        
        result = await self.db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            return None
        
        # Update fields
        for field, value in updates.items():
            if hasattr(appointment, field):
                setattr(appointment, field, value)
        
        await self.db.commit()
        await self.db.refresh(appointment)
        
        logger.info(f"Updated appointment {appointment_id}")
        
        return appointment
    
    async def delete_appointment(self, appointment_id: UUID) -> bool:
        """Delete an appointment."""
        
        result = await self.db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            return False
        
        await self.db.delete(appointment)
        await self.db.commit()
        
        logger.info(f"Deleted appointment {appointment_id}")
        
        return True
    
    async def get_appointments_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Appointment]:
        """Get appointments within a date range."""
        
        query = select(Appointment).where(
            and_(
                Appointment.start_utc >= start_date,
                Appointment.end_utc <= end_date
            )
        ).order_by(Appointment.start_utc).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
