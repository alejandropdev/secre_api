"""Patient CRUD endpoints."""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_logger, get_request_context
from app.db.session import get_db
from app.middleware.auth import TenantContext, get_current_tenant
from app.schemas.patient import (
    PatientCreateSchema,
    PatientDeleteSchema,
    PatientListResponseSchema,
    PatientResponseSchema,
    PatientSearchSchema,
    PatientUpdateSchema,
)
from app.schemas.pagination import PaginatedResponse
from app.services.patient_service import PatientService
from app.utils.schema_conversion import convert_patients_to_response_list

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreateSchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
    request_context: dict = Depends(get_request_context),
    logger: logging.Logger = Depends(get_logger),
):
    """Create a new patient."""
    
    patient_service = PatientService(db)
    
    # Create patient with enhanced error handling
    patient = await patient_service.create_patient(
        tenant_id=UUID(current_tenant.tenant_id),
        first_name=patient_data.first_name,
        first_last_name=patient_data.first_last_name,
        birth_date=patient_data.birth_date,
        gender_id=patient_data.gender_id,
        document_type_id=patient_data.document_type_id,
        document_number=patient_data.document_number,
        second_name=patient_data.second_name,
        second_last_name=patient_data.second_last_name,
        phone=patient_data.phone,
        cell_phone=patient_data.cell_phone,
        email=patient_data.email,
        eps_id=patient_data.eps_id,
        habeas_data=patient_data.habeas_data,
        custom_fields=patient_data.custom_fields,
        request_context=request_context,
    )
    
    logger.info(f"Successfully created patient {patient.id}")
    
    return convert_patients_to_response_list([patient])[0]


@router.get("/{patient_id}", response_model=PatientResponseSchema)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get patient by ID."""
    
    patient_service = PatientService(db)
    patient = await patient_service.get_patient_by_id(patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return convert_patients_to_response_list([patient])[0]


@router.patch("/{patient_id}", response_model=PatientResponseSchema)
async def update_patient(
    patient_id: UUID,
    patient_data: PatientUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Update patient information."""
    
    patient_service = PatientService(db)
    audit_service = AuditService(db)
    
    # Get existing patient for audit trail
    existing_patient = await patient_service.get_patient_by_id(patient_id)
    if not existing_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Prepare update data
    update_data = patient_data.dict(exclude_unset=True, exclude={'event_type', 'action_type'})
    
    # Check if document number is being changed and if it conflicts
    if 'document_number' in update_data or 'document_type_id' in update_data:
        doc_type_id = update_data.get('document_type_id', existing_patient.document_type_id)
        doc_number = update_data.get('document_number', existing_patient.document_number)
        
        conflicting_patient = await patient_service.get_patient_by_document(
            document_type_id=doc_type_id,
            document_number=doc_number
        )
        
        if conflicting_patient and conflicting_patient.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another patient with this document already exists"
            )
    
    # Update patient
    updated_patient = await patient_service.update_patient(patient_id, **update_data)
    
    if not updated_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update patient"
        )
    
    # Log audit trail
    await audit_service.log_action(
        tenant_id=UUID(current_tenant.tenant_id),
        resource_type="patient",
        resource_id=patient_id,
        action="update",
        api_key_id=UUID(current_tenant.api_key_id),
        before_snapshot={
            "first_name": existing_patient.first_name,
            "first_last_name": existing_patient.first_last_name,
            "document_number": existing_patient.document_number,
            "email": existing_patient.email,
            "custom_fields": existing_patient.custom_fields,
        },
        after_snapshot=update_data,
    )
    
    logger.info(f"Updated patient {patient_id} for tenant {current_tenant.tenant_id}")
    
    return convert_patients_to_response_list([updated_patient])[0]


@router.delete("/{patient_id}", response_model=dict)
async def delete_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Delete a patient."""
    
    patient_service = PatientService(db)
    audit_service = AuditService(db)
    
    # Get existing patient for audit trail
    existing_patient = await patient_service.get_patient_by_id(patient_id)
    if not existing_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Delete patient
    success = await patient_service.delete_patient(patient_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete patient"
        )
    
    # Log audit trail
    await audit_service.log_action(
        tenant_id=UUID(current_tenant.tenant_id),
        resource_type="patient",
        resource_id=patient_id,
        action="delete",
        api_key_id=UUID(current_tenant.api_key_id),
        before_snapshot={
            "first_name": existing_patient.first_name,
            "first_last_name": existing_patient.first_last_name,
            "document_number": existing_patient.document_number,
            "email": existing_patient.email,
            "custom_fields": existing_patient.custom_fields,
        },
    )
    
    logger.info(f"Deleted patient {patient_id} for tenant {current_tenant.tenant_id}")
    
    return {"message": "Patient deleted successfully"}


@router.get("/", response_model=PatientListResponseSchema)
async def search_patients(
    document_type_id: int = Query(None, description="Filter by document type ID"),
    document_number: str = Query(None, description="Filter by document number"),
    email: str = Query(None, description="Filter by email"),
    phone: str = Query(None, description="Filter by phone"),
    cell_phone: str = Query(None, description="Filter by cell phone"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Search patients with filters and pagination."""
    
    patient_service = PatientService(db)
    
    # Search patients
    patients = await patient_service.search_patients(
        document_type_id=document_type_id,
        document_number=document_number,
        email=email,
        phone=phone,
        cell_phone=cell_phone,
        limit=size,
        offset=(page - 1) * size,
    )
    
    # Get total count for pagination (simplified - in production, implement proper count query)
    total_patients = await patient_service.search_patients(
        document_type_id=document_type_id,
        document_number=document_number,
        email=email,
        phone=phone,
        cell_phone=cell_phone,
        limit=1000,  # Large limit to get total count
        offset=0,
    )
    
    total = len(total_patients)
    has_next = (page * size) < total
    has_prev = page > 1
    
    return PatientListResponseSchema(
        patients=convert_patients_to_response_list(patients),
        total=total,
        page=page,
        size=size,
        has_next=has_next,
        has_prev=has_prev,
    )


@router.get("/search", response_model=PatientListResponseSchema)
async def search_patients_advanced(
    search_params: PatientSearchSchema = Depends(),
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Advanced patient search with structured parameters."""
    
    patient_service = PatientService(db)
    
    # Search patients
    patients = await patient_service.search_patients(
        document_type_id=search_params.document_type_id,
        document_number=search_params.document_number,
        email=search_params.email,
        phone=search_params.phone,
        cell_phone=search_params.cell_phone,
        limit=search_params.size,
        offset=(search_params.page - 1) * search_params.size,
    )
    
    # Get total count for pagination
    total_patients = await patient_service.search_patients(
        document_type_id=search_params.document_type_id,
        document_number=search_params.document_number,
        email=search_params.email,
        phone=search_params.phone,
        cell_phone=search_params.cell_phone,
        limit=1000,
        offset=0,
    )
    
    total = len(total_patients)
    has_next = (search_params.page * search_params.size) < total
    has_prev = search_params.page > 1
    
    return PatientListResponseSchema(
        patients=convert_patients_to_response_list(patients),
        total=total,
        page=search_params.page,
        size=search_params.size,
        has_next=has_next,
        has_prev=has_prev,
    )
