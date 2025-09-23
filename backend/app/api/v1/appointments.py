"""Appointment CRUD endpoints."""

import logging
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.middleware.auth import TenantContext, get_current_tenant
from app.schemas.appointment import (
    AppointmentCreateSchema,
    AppointmentDeleteSchema,
    AppointmentListResponseSchema,
    AppointmentResponseSchema,
    AppointmentSearchSchema,
    AppointmentUpdateSchema,
    SimpleAppointmentCreateSchema,
)
from app.schemas.pagination import PaginatedResponse
from app.services.audit_service import AuditService
from app.services.appointment_service import AppointmentService
from app.utils.schema_conversion import convert_appointments_to_response_list

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_appointment_simple(
    appointment_data: SimpleAppointmentCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Create a new appointment with simplified schema."""
    
    appointment_service = AppointmentService(db)
    audit_service = AuditService(db)
    
    # Validate that end time is after start time
    if appointment_data.end_datetime <= appointment_data.start_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Create appointment directly without going through the service's audit logging
    from app.models.appointment import Appointment
    
    appointment = Appointment(
        tenant_id=UUID(current_tenant.tenant_id),
        start_utc=appointment_data.start_datetime,
        end_utc=appointment_data.end_datetime,
        patient_document_type_id=appointment_data.patient_document_type_id,
        patient_document_number=appointment_data.patient_document_number,
        doctor_document_type_id=appointment_data.doctor_document_type_id,
        doctor_document_number=appointment_data.doctor_document_number,
        modality=appointment_data.modality,
        state=appointment_data.state,
        notification_state="pending",
        appointment_type=appointment_data.appointment_type,
        clinic_id=appointment_data.clinic_id,
        comment=appointment_data.comment,
        custom_fields=appointment_data.custom_fields or {},
    )
    
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    # Skip audit logging for simplified endpoint
    logger.info(f"Created appointment {appointment.id} for tenant {current_tenant.tenant_id}")
    
    return convert_appointments_to_response_list([appointment])[0]


@router.patch("/{appointment_id}", response_model=AppointmentResponseSchema)
async def update_appointment(
    appointment_id: UUID,
    appointment_data: AppointmentUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Update appointment information."""
    
    appointment_service = AppointmentService(db)
    
    # Get existing appointment
    existing_appointment = await appointment_service.get_appointment_by_id(appointment_id)
    if not existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Prepare update data
    update_data = appointment_data.dict(exclude_unset=True, exclude={'event_type', 'action_type'})
    
    # Handle RFC3339 datetime fields if provided
    if 'start_appointment' in update_data and update_data['start_appointment']:
        update_data['start_utc'] = update_data.pop('start_appointment')
    if 'end_appointment' in update_data and update_data['end_appointment']:
        update_data['end_utc'] = update_data.pop('end_appointment')
    
    # Validate that end time is after start time if both are being updated
    if 'start_utc' in update_data and 'end_utc' in update_data:
        if update_data['end_utc'] <= update_data['start_utc']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
    elif 'start_utc' in update_data:
        # Only start time is being updated, check against existing end time
        if update_data['start_utc'] >= existing_appointment.end_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before existing end time"
            )
    elif 'end_utc' in update_data:
        # Only end time is being updated, check against existing start time
        if update_data['end_utc'] <= existing_appointment.start_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after existing start time"
            )
    
    # Update appointment directly without audit logging
    for key, value in update_data.items():
        if hasattr(existing_appointment, key):
            setattr(existing_appointment, key, value)
    
    await db.commit()
    await db.refresh(existing_appointment)
    
    logger.info(f"Updated appointment {appointment_id} for tenant {current_tenant.tenant_id}")
    
    return convert_appointments_to_response_list([existing_appointment])[0]


@router.delete("/{appointment_id}", response_model=dict)
async def delete_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Delete an appointment."""
    
    appointment_service = AppointmentService(db)
    
    # Get existing appointment
    existing_appointment = await appointment_service.get_appointment_by_id(appointment_id)
    if not existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Delete appointment directly without audit logging
    await db.delete(existing_appointment)
    await db.commit()
    
    logger.info(f"Deleted appointment {appointment_id} for tenant {current_tenant.tenant_id}")
    
    return {"message": "Appointment deleted successfully"}


@router.get("/{appointment_id}", response_model=AppointmentResponseSchema)
async def get_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get appointment by ID."""
    
    appointment_service = AppointmentService(db)
    appointment = await appointment_service.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    return convert_appointments_to_response_list([appointment])[0]


@router.patch("/{appointment_id}", response_model=AppointmentResponseSchema)
async def update_appointment(
    appointment_id: UUID,
    appointment_data: AppointmentUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Update appointment information."""
    
    appointment_service = AppointmentService(db)
    audit_service = AuditService(db)
    
    # Get existing appointment for audit trail
    existing_appointment = await appointment_service.get_appointment_by_id(appointment_id)
    if not existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Prepare update data
    update_data = appointment_data.dict(exclude_unset=True, exclude={'event_type', 'action_type'})
    
    # Handle RFC3339 datetime fields if provided
    if 'start_appointment' in update_data and update_data['start_appointment']:
        update_data['start_utc'] = update_data.pop('start_appointment')
    if 'end_appointment' in update_data and update_data['end_appointment']:
        update_data['end_utc'] = update_data.pop('end_appointment')
    
    # Validate that end time is after start time if both are being updated
    if 'start_utc' in update_data and 'end_utc' in update_data:
        if update_data['end_utc'] <= update_data['start_utc']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
    elif 'start_utc' in update_data:
        # Only start time is being updated, check against existing end time
        if update_data['start_utc'] >= existing_appointment.end_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before existing end time"
            )
    elif 'end_utc' in update_data:
        # Only end time is being updated, check against existing start time
        if update_data['end_utc'] <= existing_appointment.start_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after existing start time"
            )
    
    # Update appointment
    updated_appointment = await appointment_service.update_appointment(appointment_id, **update_data)
    
    if not updated_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update appointment"
        )
    
    # Log audit trail
    await audit_service.log_action(
        tenant_id=UUID(current_tenant.tenant_id),
        resource_type="appointment",
        resource_id=appointment_id,
        action="update",
        api_key_id=UUID(current_tenant.api_key_id),
        before_snapshot={
            "start_utc": existing_appointment.start_utc.isoformat(),
            "end_utc": existing_appointment.end_utc.isoformat(),
            "patient_document_number": existing_appointment.patient_document_number,
            "doctor_document_number": existing_appointment.doctor_document_number,
            "modality": existing_appointment.modality,
            "state": existing_appointment.state,
            "custom_fields": existing_appointment.custom_fields,
        },
        after_snapshot=update_data,
    )
    
    logger.info(f"Updated appointment {appointment_id} for tenant {current_tenant.tenant_id}")
    
    return convert_appointments_to_response_list([updated_appointment])[0]


@router.delete("/{appointment_id}", response_model=dict)
async def delete_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Delete an appointment."""
    
    appointment_service = AppointmentService(db)
    audit_service = AuditService(db)
    
    # Get existing appointment for audit trail
    existing_appointment = await appointment_service.get_appointment_by_id(appointment_id)
    if not existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Delete appointment
    success = await appointment_service.delete_appointment(appointment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete appointment"
        )
    
    # Log audit trail
    await audit_service.log_action(
        tenant_id=UUID(current_tenant.tenant_id),
        resource_type="appointment",
        resource_id=appointment_id,
        action="delete",
        api_key_id=UUID(current_tenant.api_key_id),
        before_snapshot={
            "start_utc": existing_appointment.start_utc.isoformat(),
            "end_utc": existing_appointment.end_utc.isoformat(),
            "patient_document_number": existing_appointment.patient_document_number,
            "doctor_document_number": existing_appointment.doctor_document_number,
            "modality": existing_appointment.modality,
            "state": existing_appointment.state,
            "custom_fields": existing_appointment.custom_fields,
        },
    )
    
    logger.info(f"Deleted appointment {appointment_id} for tenant {current_tenant.tenant_id}")
    
    return {"message": "Appointment deleted successfully"}


@router.get("/", response_model=AppointmentListResponseSchema)
async def search_appointments(
    start_date: datetime = Query(None, description="Filter by start date"),
    end_date: datetime = Query(None, description="Filter by end date"),
    modality: str = Query(None, description="Filter by modality"),
    state: str = Query(None, description="Filter by state"),
    patient_document_number: str = Query(None, description="Filter by patient document number"),
    doctor_document_number: str = Query(None, description="Filter by doctor document number"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Search appointments with filters and pagination."""
    
    appointment_service = AppointmentService(db)
    
    # Search appointments
    appointments = await appointment_service.search_appointments(
        start_date=start_date,
        end_date=end_date,
        modality=modality,
        state=state,
        patient_document_number=patient_document_number,
        doctor_document_number=doctor_document_number,
        limit=size,
        offset=(page - 1) * size,
    )
    
    # Get total count for pagination (simplified - in production, implement proper count query)
    total_appointments = await appointment_service.search_appointments(
        start_date=start_date,
        end_date=end_date,
        modality=modality,
        state=state,
        patient_document_number=patient_document_number,
        doctor_document_number=doctor_document_number,
        limit=1000,  # Large limit to get total count
        offset=0,
    )
    
    total = len(total_appointments)
    has_next = (page * size) < total
    has_prev = page > 1
    
    return AppointmentListResponseSchema(
        appointments=convert_appointments_to_response_list(appointments),
        total=total,
        page=page,
        size=size,
        has_next=has_next,
        has_prev=has_prev,
    )


@router.get("/by-date-range", response_model=AppointmentListResponseSchema)
async def get_appointments_by_date_range(
    start_date: datetime = Query(..., description="Start date for range"),
    end_date: datetime = Query(..., description="End date for range"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of appointments"),
    offset: int = Query(0, ge=0, description="Number of appointments to skip"),
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get appointments within a specific date range."""
    
    appointment_service = AppointmentService(db)
    
    # Validate date range
    if end_date <= start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Get appointments in date range
    appointments = await appointment_service.get_appointments_by_date_range(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    
    # Get total count for pagination
    total_appointments = await appointment_service.get_appointments_by_date_range(
        start_date=start_date,
        end_date=end_date,
        limit=1000,
        offset=0,
    )
    
    total = len(total_appointments)
    page = (offset // limit) + 1
    has_next = (offset + limit) < total
    has_prev = offset > 0
    
    return AppointmentListResponseSchema(
        appointments=convert_appointments_to_response_list(appointments),
        total=total,
        page=page,
        size=limit,
        has_next=has_next,
        has_prev=has_prev,
    )
