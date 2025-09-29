"""Lookup service for managing reference data."""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lookup import (
    AppointmentModality,
    AppointmentState,
    DocumentType,
    Gender,
)

logger = logging.getLogger(__name__)


class LookupService:
    """Service for managing lookup/reference data."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Document Types
    async def get_document_types(self) -> List[DocumentType]:
        """Get all document types."""
        result = await self.db.execute(
            select(DocumentType).order_by(DocumentType.name)
        )
        return result.scalars().all()
    
    async def get_document_type_by_code(self, code: str) -> Optional[DocumentType]:
        """Get document type by code."""
        result = await self.db.execute(
            select(DocumentType).where(DocumentType.code == code)
        )
        return result.scalar_one_or_none()
    
    # Genders
    async def get_genders(self) -> List[Gender]:
        """Get all genders."""
        result = await self.db.execute(
            select(Gender).order_by(Gender.name)
        )
        return result.scalars().all()
    
    async def get_gender_by_code(self, code: str) -> Optional[Gender]:
        """Get gender by code."""
        result = await self.db.execute(
            select(Gender).where(Gender.code == code)
        )
        return result.scalar_one_or_none()
    
    # Appointment Modalities
    async def get_appointment_modalities(self) -> List[AppointmentModality]:
        """Get all appointment modalities."""
        result = await self.db.execute(
            select(AppointmentModality).order_by(AppointmentModality.name)
        )
        return result.scalars().all()
    
    async def get_appointment_modality_by_code(self, code: str) -> Optional[AppointmentModality]:
        """Get appointment modality by code."""
        result = await self.db.execute(
            select(AppointmentModality).where(AppointmentModality.code == code)
        )
        return result.scalar_one_or_none()
    
    # Appointment States
    async def get_appointment_states(self) -> List[AppointmentState]:
        """Get all appointment states."""
        result = await self.db.execute(
            select(AppointmentState).order_by(AppointmentState.name)
        )
        return result.scalars().all()
    
    async def get_appointment_state_by_code(self, code: str) -> Optional[AppointmentState]:
        """Get appointment state by code."""
        result = await self.db.execute(
            select(AppointmentState).where(AppointmentState.code == code)
        )
        return result.scalar_one_or_none()
