"""Doctor availability endpoints for calendar management."""

import logging
from datetime import datetime, time
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.middleware.auth import TenantContext, get_current_tenant
from app.schemas.doctor_availability import (
    AvailableTimeSlotsResponseSchema,
    DoctorAvailabilityCreateSchema,
    DoctorAvailabilityResponseSchema,
    DoctorBlockedTimeCreateSchema,
    DoctorBlockedTimeResponseSchema,
    TimeSlotSchema,
)
from app.services.doctor_availability_service import DoctorAvailabilityService

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/doctor-availability", tags=["Doctor Availability"])


@router.post("/availability", response_model=DoctorAvailabilityResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_doctor_availability(
    availability_data: DoctorAvailabilityCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Create doctor availability for a specific day of week."""
    
    availability_service = DoctorAvailabilityService(db)
    
    # Parse time strings
    try:
        start_time = time.fromisoformat(availability_data.start_time)
        end_time = time.fromisoformat(availability_data.end_time)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format. Use HH:MM format (e.g., 09:00)"
        )
    
    # Validate time range
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )
    
    availability = await availability_service.create_availability(
        tenant_id=UUID(current_tenant.tenant_id),
        doctor_document_type_id=availability_data.doctor_document_type_id,
        doctor_document_number=availability_data.doctor_document_number,
        day_of_week=availability_data.day_of_week,
        start_time=start_time,
        end_time=end_time,
        appointment_duration_minutes=availability_data.appointment_duration_minutes,
        custom_fields=availability_data.custom_fields,
    )
    
    logger.info(f"Created availability for doctor {availability_data.doctor_document_number}")
    
    return DoctorAvailabilityResponseSchema(
        id=availability.id,
        tenant_id=availability.tenant_id,
        doctor_document_type_id=availability.doctor_document_type_id,
        doctor_document_number=availability.doctor_document_number,
        day_of_week=availability.day_of_week,
        start_time=availability.start_time.isoformat(),
        end_time=availability.end_time.isoformat(),
        appointment_duration_minutes=availability.appointment_duration_minutes,
        is_active=availability.is_active,
        custom_fields=availability.custom_fields,
        created_at=availability.created_at,
        updated_at=availability.updated_at,
    )


@router.post("/blocked-time", response_model=DoctorBlockedTimeResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_blocked_time(
    blocked_data: DoctorBlockedTimeCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Create blocked time for a doctor."""
    
    availability_service = DoctorAvailabilityService(db)
    
    # Parse datetime strings
    try:
        start_datetime = datetime.fromisoformat(blocked_data.start_datetime.replace('Z', '+00:00'))
        end_datetime = datetime.fromisoformat(blocked_data.end_datetime.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format (e.g., 2024-01-15T10:00:00)"
        )
    
    # Validate datetime range
    if start_datetime >= end_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start datetime must be before end datetime"
        )
    
    blocked_time = await availability_service.create_blocked_time(
        tenant_id=UUID(current_tenant.tenant_id),
        doctor_document_type_id=blocked_data.doctor_document_type_id,
        doctor_document_number=blocked_data.doctor_document_number,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        reason=blocked_data.reason,
        custom_fields=blocked_data.custom_fields,
    )
    
    logger.info(f"Created blocked time for doctor {blocked_data.doctor_document_number}")
    
    return DoctorBlockedTimeResponseSchema(
        id=blocked_time.id,
        tenant_id=blocked_time.tenant_id,
        doctor_document_type_id=blocked_time.doctor_document_type_id,
        doctor_document_number=blocked_time.doctor_document_number,
        start_datetime=blocked_time.start_datetime,
        end_datetime=blocked_time.end_datetime,
        reason=blocked_time.reason,
        is_active=blocked_time.is_active,
        custom_fields=blocked_time.custom_fields,
        created_at=blocked_time.created_at,
        updated_at=blocked_time.updated_at,
    )


@router.get("/availability/{doctor_document_type_id}/{doctor_document_number}", response_model=List[DoctorAvailabilityResponseSchema])
async def get_doctor_availability(
    doctor_document_type_id: int,
    doctor_document_number: str,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get all availability for a doctor."""
    
    availability_service = DoctorAvailabilityService(db)
    
    availability_list = await availability_service.get_doctor_availability(
        tenant_id=UUID(current_tenant.tenant_id),
        doctor_document_type_id=doctor_document_type_id,
        doctor_document_number=doctor_document_number,
    )
    
    return [
        DoctorAvailabilityResponseSchema(
            id=av.id,
            tenant_id=av.tenant_id,
            doctor_document_type_id=av.doctor_document_type_id,
            doctor_document_number=av.doctor_document_number,
            day_of_week=av.day_of_week,
            start_time=av.start_time.isoformat(),
            end_time=av.end_time.isoformat(),
            appointment_duration_minutes=av.appointment_duration_minutes,
            is_active=av.is_active,
            custom_fields=av.custom_fields,
            created_at=av.created_at,
            updated_at=av.updated_at,
        )
        for av in availability_list
    ]


@router.patch("/availability/{availability_id}", response_model=DoctorAvailabilityResponseSchema)
async def update_doctor_availability(
    availability_id: UUID,
    availability_data: DoctorAvailabilityCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Update doctor availability."""
    
    availability_service = DoctorAvailabilityService(db)
    
    # Parse time strings
    try:
        start_time = time.fromisoformat(availability_data.start_time)
        end_time = time.fromisoformat(availability_data.end_time)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format. Use HH:MM format (e.g., 09:00)"
        )
    
    # Validate time range
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )
    
    # Get existing availability
    from sqlalchemy import select
    from app.models.doctor_availability import DoctorAvailability
    
    result = await db.execute(
        select(DoctorAvailability)
        .where(
            DoctorAvailability.id == availability_id,
            DoctorAvailability.tenant_id == UUID(current_tenant.tenant_id)
        )
    )
    availability = result.scalar_one_or_none()
    
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability not found"
        )
    
    # Update availability
    availability.doctor_document_type_id = availability_data.doctor_document_type_id
    availability.doctor_document_number = availability_data.doctor_document_number
    availability.day_of_week = availability_data.day_of_week
    availability.start_time = start_time
    availability.end_time = end_time
    availability.appointment_duration_minutes = availability_data.appointment_duration_minutes
    availability.custom_fields = availability_data.custom_fields
    
    await db.commit()
    await db.refresh(availability)
    
    logger.info(f"Updated availability {availability_id}")
    
    return DoctorAvailabilityResponseSchema(
        id=availability.id,
        tenant_id=availability.tenant_id,
        doctor_document_type_id=availability.doctor_document_type_id,
        doctor_document_number=availability.doctor_document_number,
        day_of_week=availability.day_of_week,
        start_time=availability.start_time.isoformat(),
        end_time=availability.end_time.isoformat(),
        appointment_duration_minutes=availability.appointment_duration_minutes,
        is_active=availability.is_active,
        custom_fields=availability.custom_fields,
        created_at=availability.created_at,
        updated_at=availability.updated_at,
    )


@router.delete("/availability/{availability_id}", response_model=dict)
async def delete_doctor_availability(
    availability_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Delete doctor availability."""
    
    from sqlalchemy import select
    from app.models.doctor_availability import DoctorAvailability
    
    result = await db.execute(
        select(DoctorAvailability)
        .where(
            DoctorAvailability.id == availability_id,
            DoctorAvailability.tenant_id == UUID(current_tenant.tenant_id)
        )
    )
    availability = result.scalar_one_or_none()
    
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability not found"
        )
    
    await db.delete(availability)
    await db.commit()
    
    logger.info(f"Deleted availability {availability_id}")
    
    return {"message": "Availability deleted successfully"}


@router.get("/time-slots/{doctor_document_type_id}/{doctor_document_number}", response_model=AvailableTimeSlotsResponseSchema)
async def get_available_time_slots(
    doctor_document_type_id: int,
    doctor_document_number: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get available time slots for a doctor on a specific date."""
    
    availability_service = DoctorAvailabilityService(db)
    
    # Parse date
    try:
        target_date = datetime.fromisoformat(date).date()
        target_datetime = datetime.combine(target_date, datetime.min.time())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD format (e.g., 2024-01-15)"
        )
    
    time_slots = await availability_service.get_available_time_slots(
        tenant_id=UUID(current_tenant.tenant_id),
        doctor_document_type_id=doctor_document_type_id,
        doctor_document_number=doctor_document_number,
        date=target_datetime,
    )
    
    available_slots = [slot for slot in time_slots if slot["available"]]
    
    return AvailableTimeSlotsResponseSchema(
        doctor_document_type_id=doctor_document_type_id,
        doctor_document_number=doctor_document_number,
        date=date,
        time_slots=[
            TimeSlotSchema(
                start_datetime=slot["start_datetime"],
                end_datetime=slot["end_datetime"],
                available=slot["available"],
            )
            for slot in time_slots
        ],
        total_slots=len(time_slots),
        available_slots=len(available_slots),
    )


@router.get("/check-availability/{doctor_document_type_id}/{doctor_document_number}")
async def check_time_availability(
    doctor_document_type_id: int,
    doctor_document_number: str,
    start_datetime: str = Query(..., description="Start datetime in ISO format"),
    end_datetime: str = Query(..., description="End datetime in ISO format"),
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Check if a specific time slot is available for a doctor."""
    
    availability_service = DoctorAvailabilityService(db)
    
    # Parse datetime strings
    try:
        start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format (e.g., 2024-01-15T10:00:00)"
        )
    
    is_available = await availability_service.is_time_available(
        tenant_id=UUID(current_tenant.tenant_id),
        doctor_document_type_id=doctor_document_type_id,
        doctor_document_number=doctor_document_number,
        start_datetime=start_dt,
        end_datetime=end_dt,
    )
    
    return {
        "available": is_available,
        "doctor_document_type_id": doctor_document_type_id,
        "doctor_document_number": doctor_document_number,
        "start_datetime": start_dt.isoformat(),
        "end_datetime": end_dt.isoformat(),
    }


@router.get("/blocked-time/{doctor_document_type_id}/{doctor_document_number}", response_model=List[DoctorBlockedTimeResponseSchema])
async def get_blocked_times(
    doctor_document_type_id: int,
    doctor_document_number: str,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get all blocked times for a doctor."""
    
    from sqlalchemy import select
    from app.models.doctor_availability import DoctorBlockedTime
    
    result = await db.execute(
        select(DoctorBlockedTime)
        .where(
            DoctorBlockedTime.tenant_id == UUID(current_tenant.tenant_id),
            DoctorBlockedTime.doctor_document_type_id == doctor_document_type_id,
            DoctorBlockedTime.doctor_document_number == doctor_document_number,
            DoctorBlockedTime.is_active == True,
        )
        .order_by(DoctorBlockedTime.start_datetime)
    )
    
    blocked_times = result.scalars().all()
    
    return [
        DoctorBlockedTimeResponseSchema(
            id=bt.id,
            tenant_id=bt.tenant_id,
            doctor_document_type_id=bt.doctor_document_type_id,
            doctor_document_number=bt.doctor_document_number,
            start_datetime=bt.start_datetime,
            end_datetime=bt.end_datetime,
            reason=bt.reason,
            is_active=bt.is_active,
            custom_fields=bt.custom_fields,
            created_at=bt.created_at,
            updated_at=bt.updated_at,
        )
        for bt in blocked_times
    ]


@router.patch("/blocked-time/{blocked_time_id}", response_model=DoctorBlockedTimeResponseSchema)
async def update_blocked_time(
    blocked_time_id: UUID,
    blocked_data: DoctorBlockedTimeCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Update blocked time."""
    
    # Parse datetime strings
    try:
        start_datetime = datetime.fromisoformat(blocked_data.start_datetime.replace('Z', '+00:00'))
        end_datetime = datetime.fromisoformat(blocked_data.end_datetime.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format (e.g., 2024-01-15T10:00:00)"
        )
    
    # Validate datetime range
    if start_datetime >= end_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start datetime must be before end datetime"
        )
    
    # Get existing blocked time
    from sqlalchemy import select
    from app.models.doctor_availability import DoctorBlockedTime
    
    result = await db.execute(
        select(DoctorBlockedTime)
        .where(
            DoctorBlockedTime.id == blocked_time_id,
            DoctorBlockedTime.tenant_id == UUID(current_tenant.tenant_id)
        )
    )
    blocked_time = result.scalar_one_or_none()
    
    if not blocked_time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blocked time not found"
        )
    
    # Update blocked time
    blocked_time.doctor_document_type_id = blocked_data.doctor_document_type_id
    blocked_time.doctor_document_number = blocked_data.doctor_document_number
    blocked_time.start_datetime = start_datetime
    blocked_time.end_datetime = end_datetime
    blocked_time.reason = blocked_data.reason
    blocked_time.custom_fields = blocked_data.custom_fields
    
    await db.commit()
    await db.refresh(blocked_time)
    
    logger.info(f"Updated blocked time {blocked_time_id}")
    
    return DoctorBlockedTimeResponseSchema(
        id=blocked_time.id,
        tenant_id=blocked_time.tenant_id,
        doctor_document_type_id=blocked_time.doctor_document_type_id,
        doctor_document_number=blocked_time.doctor_document_number,
        start_datetime=blocked_time.start_datetime,
        end_datetime=blocked_time.end_datetime,
        reason=blocked_time.reason,
        is_active=blocked_time.is_active,
        custom_fields=blocked_time.custom_fields,
        created_at=blocked_time.created_at,
        updated_at=blocked_time.updated_at,
    )


@router.delete("/blocked-time/{blocked_time_id}", response_model=dict)
async def delete_blocked_time(
    blocked_time_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Delete blocked time."""
    
    from sqlalchemy import select
    from app.models.doctor_availability import DoctorBlockedTime
    
    result = await db.execute(
        select(DoctorBlockedTime)
        .where(
            DoctorBlockedTime.id == blocked_time_id,
            DoctorBlockedTime.tenant_id == UUID(current_tenant.tenant_id)
        )
    )
    blocked_time = result.scalar_one_or_none()
    
    if not blocked_time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blocked time not found"
        )
    
    await db.delete(blocked_time)
    await db.commit()
    
    logger.info(f"Deleted blocked time {blocked_time_id}")
    
    return {"message": "Blocked time deleted successfully"}
