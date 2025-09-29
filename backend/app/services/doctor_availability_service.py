"""Doctor availability service for managing calendar and time slots."""

import logging
from datetime import datetime, time, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doctor_availability import DoctorAvailability, DoctorBlockedTime
from app.models.appointment import Appointment

logger = logging.getLogger(__name__)


class DoctorAvailabilityService:
    """Service for managing doctor availability and time slots."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_availability(
        self,
        tenant_id: UUID,
        doctor_document_type_id: int,
        doctor_document_number: str,
        day_of_week: int,
        start_time: time,
        end_time: time,
        appointment_duration_minutes: int = 30,
        custom_fields: Optional[dict] = None,
    ) -> DoctorAvailability:
        """Create doctor availability for a specific day of week."""
        
        availability = DoctorAvailability(
            tenant_id=tenant_id,
            doctor_document_type_id=doctor_document_type_id,
            doctor_document_number=doctor_document_number,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            appointment_duration_minutes=appointment_duration_minutes,
            custom_fields=custom_fields or {},
        )
        
        self.db.add(availability)
        await self.db.commit()
        await self.db.refresh(availability)
        
        logger.info(f"Created availability for doctor {doctor_document_number} on day {day_of_week}")
        
        return availability
    
    async def create_blocked_time(
        self,
        tenant_id: UUID,
        doctor_document_type_id: int,
        doctor_document_number: str,
        start_datetime: datetime,
        end_datetime: datetime,
        reason: Optional[str] = None,
        custom_fields: Optional[dict] = None,
    ) -> DoctorBlockedTime:
        """Create blocked time for a doctor."""
        
        blocked_time = DoctorBlockedTime(
            tenant_id=tenant_id,
            doctor_document_type_id=doctor_document_type_id,
            doctor_document_number=doctor_document_number,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            reason=reason,
            custom_fields=custom_fields or {},
        )
        
        self.db.add(blocked_time)
        await self.db.commit()
        await self.db.refresh(blocked_time)
        
        logger.info(f"Created blocked time for doctor {doctor_document_number}")
        
        return blocked_time
    
    async def get_doctor_availability(
        self,
        tenant_id: UUID,
        doctor_document_type_id: int,
        doctor_document_number: str,
    ) -> List[DoctorAvailability]:
        """Get all availability for a doctor."""
        
        result = await self.db.execute(
            select(DoctorAvailability)
            .where(
                and_(
                    DoctorAvailability.tenant_id == tenant_id,
                    DoctorAvailability.doctor_document_type_id == doctor_document_type_id,
                    DoctorAvailability.doctor_document_number == doctor_document_number,
                    DoctorAvailability.is_active == True,
                )
            )
            .order_by(DoctorAvailability.day_of_week, DoctorAvailability.start_time)
        )
        
        return result.scalars().all()
    
    async def get_available_time_slots(
        self,
        tenant_id: UUID,
        doctor_document_type_id: int,
        doctor_document_number: str,
        date: datetime,
    ) -> List[dict]:
        """Get available time slots for a doctor on a specific date."""
        
        # Get doctor's availability for this day of week
        day_of_week = date.weekday()
        availability_result = await self.db.execute(
            select(DoctorAvailability)
            .where(
                and_(
                    DoctorAvailability.tenant_id == tenant_id,
                    DoctorAvailability.doctor_document_type_id == doctor_document_type_id,
                    DoctorAvailability.doctor_document_number == doctor_document_number,
                    DoctorAvailability.day_of_week == day_of_week,
                    DoctorAvailability.is_active == True,
                )
            )
            .order_by(DoctorAvailability.start_time)
        )
        availability_records = availability_result.scalars().all()
        
        if not availability_records:
            return []
        
        # Get blocked times for this date
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        blocked_result = await self.db.execute(
            select(DoctorBlockedTime)
            .where(
                and_(
                    DoctorBlockedTime.tenant_id == tenant_id,
                    DoctorBlockedTime.doctor_document_type_id == doctor_document_type_id,
                    DoctorBlockedTime.doctor_document_number == doctor_document_number,
                    DoctorBlockedTime.is_active == True,
                    or_(
                        and_(
                            DoctorBlockedTime.start_datetime < end_of_day,
                            DoctorBlockedTime.end_datetime > start_of_day,
                        )
                    ),
                )
            )
        )
        blocked_times = blocked_result.scalars().all()
        
        # Get existing appointments for this date
        appointments_result = await self.db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.tenant_id == tenant_id,
                    Appointment.doctor_document_type_id == doctor_document_type_id,
                    Appointment.doctor_document_number == doctor_document_number,
                    Appointment.start_utc >= start_of_day,
                    Appointment.start_utc < end_of_day,
                )
            )
        )
        appointments = appointments_result.scalars().all()
        
        # Generate time slots for all availability records
        time_slots = []
        
        for availability in availability_records:
            current_time = datetime.combine(date.date(), availability.start_time)
            end_time = datetime.combine(date.date(), availability.end_time)
            duration = timedelta(minutes=availability.appointment_duration_minutes)
            
            # Make timezone-aware
            current_time = current_time.replace(tzinfo=None)
            end_time = end_time.replace(tzinfo=None)
            
            while current_time + duration <= end_time:
                slot_end = current_time + duration
                
                # Check if this slot conflicts with blocked time
                is_blocked = any(
                    current_time < bt.end_datetime and slot_end > bt.start_datetime
                    for bt in blocked_times
                )
                
                # Check if this slot conflicts with existing appointments
                is_booked = any(
                    current_time < ap.end_utc.replace(tzinfo=None) and slot_end > ap.start_utc.replace(tzinfo=None)
                    for ap in appointments
                )
                
                time_slots.append({
                    "start_datetime": current_time,
                    "end_datetime": slot_end,
                    "doctor_document_type_id": doctor_document_type_id,
                    "doctor_document_number": doctor_document_number,
                    "available": not (is_blocked or is_booked),
                })
                
                current_time += duration
        
        return time_slots
    
    async def is_time_available(
        self,
        tenant_id: UUID,
        doctor_document_type_id: int,
        doctor_document_number: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> bool:
        """Check if a specific time slot is available for a doctor."""
        
        # Check if doctor has availability on this day
        day_of_week = start_datetime.weekday()
        availability_result = await self.db.execute(
            select(DoctorAvailability)
            .where(
                and_(
                    DoctorAvailability.tenant_id == tenant_id,
                    DoctorAvailability.doctor_document_type_id == doctor_document_type_id,
                    DoctorAvailability.doctor_document_number == doctor_document_number,
                    DoctorAvailability.day_of_week == day_of_week,
                    DoctorAvailability.is_active == True,
                )
            )
        )
        availability = availability_result.scalar_one_or_none()
        
        if not availability:
            return False
        
        # Check if the requested time is within doctor's working hours
        start_time = start_datetime.time()
        end_time = end_datetime.time()
        
        if start_time < availability.start_time or end_time > availability.end_time:
            return False
        
        # Check for blocked times
        blocked_result = await self.db.execute(
            select(DoctorBlockedTime)
            .where(
                and_(
                    DoctorBlockedTime.tenant_id == tenant_id,
                    DoctorBlockedTime.doctor_document_type_id == doctor_document_type_id,
                    DoctorBlockedTime.doctor_document_number == doctor_document_number,
                    DoctorBlockedTime.is_active == True,
                    DoctorBlockedTime.start_datetime < end_datetime,
                    DoctorBlockedTime.end_datetime > start_datetime,
                )
            )
        )
        
        if blocked_result.scalar_one_or_none():
            return False
        
        # Check for existing appointments
        appointment_result = await self.db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.tenant_id == tenant_id,
                    Appointment.doctor_document_type_id == doctor_document_type_id,
                    Appointment.doctor_document_number == doctor_document_number,
                    Appointment.start_utc < end_datetime,
                    Appointment.end_utc > start_datetime,
                )
            )
        )
        
        if appointment_result.scalar_one_or_none():
            return False
        
        return True
