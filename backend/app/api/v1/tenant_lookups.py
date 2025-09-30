"""API endpoints for tenant-specific lookup data."""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_tenant
from app.db.session import get_db
from app.core.exceptions import NotFoundAPIException, ValidationAPIException
from app.middleware.auth import TenantContext
from app.schemas.tenant_lookup import (
    TenantAppointmentTypeCreateSchema,
    TenantAppointmentTypeResponseSchema,
    TenantAppointmentTypeUpdateSchema,
    TenantClinicCreateSchema,
    TenantClinicResponseSchema,
    TenantClinicUpdateSchema,
    TenantLookupListResponseSchema,
)
from app.services.tenant_lookup_service import TenantLookupService

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/tenant-lookups", tags=["Tenant Lookups"])


# Appointment Types Endpoints
@router.post("/appointment-types", response_model=TenantAppointmentTypeResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_appointment_type(
    appointment_type_data: TenantAppointmentTypeCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Create a new appointment type for the current tenant."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        appointment_type = await tenant_lookup_service.create_appointment_type(
            tenant_id=UUID(current_tenant.tenant_id),
            code=appointment_type_data.code,
            name=appointment_type_data.name,
            description=appointment_type_data.description,
            is_active=appointment_type_data.is_active,
        )
        
        return TenantAppointmentTypeResponseSchema(
            id=appointment_type.id,
            tenant_id=str(appointment_type.tenant_id),
            code=appointment_type.code,
            name=appointment_type.name,
            description=appointment_type.description,
            is_active=appointment_type.is_active,
            created_at=appointment_type.created_at.isoformat(),
            updated_at=appointment_type.updated_at.isoformat(),
        )
        
    except ValidationAPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating appointment type: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/appointment-types", response_model=List[TenantAppointmentTypeResponseSchema])
async def get_appointment_types(
    active_only: bool = Query(True, description="Only return active appointment types"),
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get all appointment types for the current tenant."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        appointment_types = await tenant_lookup_service.get_appointment_types(
            tenant_id=UUID(current_tenant.tenant_id),
            active_only=active_only,
        )
        
        return [
            TenantAppointmentTypeResponseSchema(
                id=apt.id,
                tenant_id=str(apt.tenant_id),
                code=apt.code,
                name=apt.name,
                description=apt.description,
                is_active=apt.is_active,
                created_at=apt.created_at.isoformat(),
                updated_at=apt.updated_at.isoformat(),
            )
            for apt in appointment_types
        ]
        
    except Exception as e:
        logger.error(f"Error getting appointment types: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/appointment-types/{appointment_type_id}", response_model=TenantAppointmentTypeResponseSchema)
async def get_appointment_type(
    appointment_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get a specific appointment type by ID."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        appointment_type = await tenant_lookup_service.get_appointment_type_by_id(
            tenant_id=UUID(current_tenant.tenant_id),
            appointment_type_id=appointment_type_id,
        )
        
        if not appointment_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment type not found")
        
        return TenantAppointmentTypeResponseSchema(
            id=appointment_type.id,
            tenant_id=str(appointment_type.tenant_id),
            code=appointment_type.code,
            name=appointment_type.name,
            description=appointment_type.description,
            is_active=appointment_type.is_active,
            created_at=appointment_type.created_at.isoformat(),
            updated_at=appointment_type.updated_at.isoformat(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment type: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/appointment-types/{appointment_type_id}", response_model=TenantAppointmentTypeResponseSchema)
async def update_appointment_type(
    appointment_type_id: int,
    appointment_type_data: TenantAppointmentTypeUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Update an appointment type."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = appointment_type_data.dict(exclude_unset=True)
        
        appointment_type = await tenant_lookup_service.update_appointment_type(
            tenant_id=UUID(current_tenant.tenant_id),
            appointment_type_id=appointment_type_id,
            **update_data,
        )
        
        if not appointment_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment type not found")
        
        return TenantAppointmentTypeResponseSchema(
            id=appointment_type.id,
            tenant_id=str(appointment_type.tenant_id),
            code=appointment_type.code,
            name=appointment_type.name,
            description=appointment_type.description,
            is_active=appointment_type.is_active,
            created_at=appointment_type.created_at.isoformat(),
            updated_at=appointment_type.updated_at.isoformat(),
        )
        
    except ValidationAPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment type: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/appointment-types/{appointment_type_id}", response_model=dict)
async def delete_appointment_type(
    appointment_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Delete an appointment type (soft delete)."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        success = await tenant_lookup_service.delete_appointment_type(
            tenant_id=UUID(current_tenant.tenant_id),
            appointment_type_id=appointment_type_id,
        )
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment type not found")
        
        return {"message": "Appointment type deleted successfully"}
        
    except ValidationAPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting appointment type: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Clinics Endpoints
@router.post("/clinics", response_model=TenantClinicResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_clinic(
    clinic_data: TenantClinicCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Create a new clinic for the current tenant."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        clinic = await tenant_lookup_service.create_clinic(
            tenant_id=UUID(current_tenant.tenant_id),
            code=clinic_data.code,
            name=clinic_data.name,
            description=clinic_data.description,
            address=clinic_data.address,
            phone=clinic_data.phone,
            email=clinic_data.email,
            is_active=clinic_data.is_active,
        )
        
        return TenantClinicResponseSchema(
            id=clinic.id,
            tenant_id=str(clinic.tenant_id),
            code=clinic.code,
            name=clinic.name,
            description=clinic.description,
            address=clinic.address,
            phone=clinic.phone,
            email=clinic.email,
            is_active=clinic.is_active,
            created_at=clinic.created_at.isoformat(),
            updated_at=clinic.updated_at.isoformat(),
        )
        
    except ValidationAPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating clinic: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/clinics", response_model=List[TenantClinicResponseSchema])
async def get_clinics(
    active_only: bool = Query(True, description="Only return active clinics"),
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get all clinics for the current tenant."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        clinics = await tenant_lookup_service.get_clinics(
            tenant_id=UUID(current_tenant.tenant_id),
            active_only=active_only,
        )
        
        return [
            TenantClinicResponseSchema(
                id=clinic.id,
                tenant_id=str(clinic.tenant_id),
                code=clinic.code,
                name=clinic.name,
                description=clinic.description,
                address=clinic.address,
                phone=clinic.phone,
                email=clinic.email,
                is_active=clinic.is_active,
                created_at=clinic.created_at.isoformat(),
                updated_at=clinic.updated_at.isoformat(),
            )
            for clinic in clinics
        ]
        
    except Exception as e:
        logger.error(f"Error getting clinics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/clinics/{clinic_id}", response_model=TenantClinicResponseSchema)
async def get_clinic(
    clinic_id: int,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get a specific clinic by ID."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        clinic = await tenant_lookup_service.get_clinic_by_id(
            tenant_id=UUID(current_tenant.tenant_id),
            clinic_id=clinic_id,
        )
        
        if not clinic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
        
        return TenantClinicResponseSchema(
            id=clinic.id,
            tenant_id=str(clinic.tenant_id),
            code=clinic.code,
            name=clinic.name,
            description=clinic.description,
            address=clinic.address,
            phone=clinic.phone,
            email=clinic.email,
            is_active=clinic.is_active,
            created_at=clinic.created_at.isoformat(),
            updated_at=clinic.updated_at.isoformat(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting clinic: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/clinics/{clinic_id}", response_model=TenantClinicResponseSchema)
async def update_clinic(
    clinic_id: int,
    clinic_data: TenantClinicUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Update a clinic."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = clinic_data.dict(exclude_unset=True)
        
        clinic = await tenant_lookup_service.update_clinic(
            tenant_id=UUID(current_tenant.tenant_id),
            clinic_id=clinic_id,
            **update_data,
        )
        
        if not clinic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
        
        return TenantClinicResponseSchema(
            id=clinic.id,
            tenant_id=str(clinic.tenant_id),
            code=clinic.code,
            name=clinic.name,
            description=clinic.description,
            address=clinic.address,
            phone=clinic.phone,
            email=clinic.email,
            is_active=clinic.is_active,
            created_at=clinic.created_at.isoformat(),
            updated_at=clinic.updated_at.isoformat(),
        )
        
    except ValidationAPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating clinic: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/clinics/{clinic_id}", response_model=dict)
async def delete_clinic(
    clinic_id: int,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Delete a clinic (soft delete)."""
    
    tenant_lookup_service = TenantLookupService(db)
    
    try:
        success = await tenant_lookup_service.delete_clinic(
            tenant_id=UUID(current_tenant.tenant_id),
            clinic_id=clinic_id,
        )
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
        
        return {"message": "Clinic deleted successfully"}
        
    except ValidationAPIException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting clinic: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
