"""Lookup endpoints for reference data."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.middleware.auth import TenantContext, get_current_tenant
from app.schemas.lookup import (
    AppointmentModalitySchema,
    AppointmentStateSchema,
    DocumentTypeSchema,
    GenderSchema,
    LookupListResponseSchema,
)
from app.services.lookup_service import LookupService
from app.utils.schema_conversion import (
    convert_appointment_modalities_to_schema_list,
    convert_appointment_states_to_schema_list,
    convert_document_types_to_schema_list,
    convert_genders_to_schema_list,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_v1_prefix}/lookup", tags=["Lookup"])


@router.get("/document-types", response_model=LookupListResponseSchema)
async def get_document_types(
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get all document types."""
    
    lookup_service = LookupService(db)
    document_types = await lookup_service.get_document_types()
    
    return LookupListResponseSchema(
        items=convert_document_types_to_schema_list(document_types),
        total=len(document_types),
    )


@router.get("/genders", response_model=LookupListResponseSchema)
async def get_genders(
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get all genders."""
    
    lookup_service = LookupService(db)
    genders = await lookup_service.get_genders()
    
    return LookupListResponseSchema(
        items=convert_genders_to_schema_list(genders),
        total=len(genders),
    )


@router.get("/appointment-modalities", response_model=LookupListResponseSchema)
async def get_appointment_modalities(
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get all appointment modalities."""
    
    lookup_service = LookupService(db)
    modalities = await lookup_service.get_appointment_modalities()
    
    return LookupListResponseSchema(
        items=convert_appointment_modalities_to_schema_list(modalities),
        total=len(modalities),
    )


@router.get("/appointment-states", response_model=LookupListResponseSchema)
async def get_appointment_states(
    db: AsyncSession = Depends(get_db),
    current_tenant: TenantContext = Depends(get_current_tenant),
):
    """Get all appointment states."""
    
    lookup_service = LookupService(db)
    states = await lookup_service.get_appointment_states()
    
    return LookupListResponseSchema(
        items=convert_appointment_states_to_schema_list(states),
        total=len(states),
    )
