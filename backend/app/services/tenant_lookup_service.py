"""Service for managing tenant-specific lookup data."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundAPIException, ValidationAPIException
from app.models.tenant_lookup import TenantAppointmentType, TenantClinic
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class TenantLookupService:
    """Service for managing tenant-specific lookup data."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
    
    # Tenant Appointment Types
    async def create_appointment_type(
        self,
        tenant_id: UUID,
        code: str,
        name: str,
        description: Optional[str] = None,
        is_active: str = "true",
        request_context: Optional[dict] = None,
    ) -> TenantAppointmentType:
        """Create a new tenant appointment type."""
        
        try:
            # Check if code already exists for this tenant
            existing = await self.get_appointment_type_by_code(tenant_id, code)
            if existing:
                raise ValidationAPIException(f"Appointment type with code '{code}' already exists for this tenant")
            
            appointment_type = TenantAppointmentType(
                tenant_id=tenant_id,
                code=code,
                name=name,
                description=description,
                is_active=is_active,
            )
            
            self.db.add(appointment_type)
            await self.db.commit()
            await self.db.refresh(appointment_type)
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="tenant_appointment_type",
                resource_id=appointment_type.id,
                action="create",
                after_snapshot=appointment_type.__dict__,
                request_context=request_context,
            )
            
            logger.info(f"Created appointment type {appointment_type.id} for tenant {tenant_id}")
            
            return appointment_type
            
        except ValidationAPIException:
            raise
        except Exception as e:
            logger.error(f"Error creating appointment type: {e}")
            raise ValidationAPIException(f"Failed to create appointment type: {str(e)}")
    
    async def get_appointment_type_by_id(self, tenant_id: UUID, appointment_type_id: int) -> Optional[TenantAppointmentType]:
        """Get appointment type by ID for a specific tenant."""
        result = await self.db.execute(
            select(TenantAppointmentType).where(
                and_(
                    TenantAppointmentType.id == appointment_type_id,
                    TenantAppointmentType.tenant_id == tenant_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_appointment_type_by_code(self, tenant_id: UUID, code: str) -> Optional[TenantAppointmentType]:
        """Get appointment type by code for a specific tenant."""
        result = await self.db.execute(
            select(TenantAppointmentType).where(
                and_(
                    TenantAppointmentType.code == code,
                    TenantAppointmentType.tenant_id == tenant_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_appointment_types(self, tenant_id: UUID, active_only: bool = True) -> List[TenantAppointmentType]:
        """Get all appointment types for a tenant."""
        query = select(TenantAppointmentType).where(TenantAppointmentType.tenant_id == tenant_id)
        
        if active_only:
            query = query.where(TenantAppointmentType.is_active == "true")
        
        query = query.order_by(TenantAppointmentType.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_appointment_type(
        self,
        tenant_id: UUID,
        appointment_type_id: int,
        request_context: Optional[dict] = None,
        **updates: any,
    ) -> Optional[TenantAppointmentType]:
        """Update an appointment type."""
        
        appointment_type = await self.get_appointment_type_by_id(tenant_id, appointment_type_id)
        if not appointment_type:
            raise NotFoundAPIException("Appointment type not found")
        
        try:
            # Check if code is being updated and if it already exists
            if "code" in updates and updates["code"] != appointment_type.code:
                existing = await self.get_appointment_type_by_code(tenant_id, updates["code"])
                if existing:
                    raise ValidationAPIException(f"Appointment type with code '{updates['code']}' already exists for this tenant")
            
            # Store before snapshot for audit
            before_snapshot = appointment_type.__dict__.copy()
            
            # Update fields
            for field, value in updates.items():
                if hasattr(appointment_type, field) and value is not None:
                    setattr(appointment_type, field, value)
            
            await self.db.commit()
            await self.db.refresh(appointment_type)
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="tenant_appointment_type",
                resource_id=appointment_type.id,
                action="update",
                before_snapshot=before_snapshot,
                after_snapshot=appointment_type.__dict__,
                request_context=request_context,
            )
            
            logger.info(f"Updated appointment type {appointment_type.id} for tenant {tenant_id}")
            
            return appointment_type
            
        except ValidationAPIException:
            raise
        except Exception as e:
            logger.error(f"Error updating appointment type: {e}")
            raise ValidationAPIException(f"Failed to update appointment type: {str(e)}")
    
    async def delete_appointment_type(
        self,
        tenant_id: UUID,
        appointment_type_id: int,
        request_context: Optional[dict] = None,
    ) -> bool:
        """Delete an appointment type (soft delete by setting is_active to false)."""
        
        appointment_type = await self.get_appointment_type_by_id(tenant_id, appointment_type_id)
        if not appointment_type:
            raise NotFoundAPIException("Appointment type not found")
        
        try:
            # Soft delete by setting is_active to false
            appointment_type.is_active = "false"
            await self.db.commit()
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="tenant_appointment_type",
                resource_id=appointment_type.id,
                action="delete",
                after_snapshot=appointment_type.__dict__,
                request_context=request_context,
            )
            
            logger.info(f"Deleted appointment type {appointment_type.id} for tenant {tenant_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting appointment type: {e}")
            raise ValidationAPIException(f"Failed to delete appointment type: {str(e)}")
    
    # Tenant Clinics
    async def create_clinic(
        self,
        tenant_id: UUID,
        code: str,
        name: str,
        description: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        is_active: str = "true",
        request_context: Optional[dict] = None,
    ) -> TenantClinic:
        """Create a new tenant clinic."""
        
        try:
            # Check if code already exists for this tenant
            existing = await self.get_clinic_by_code(tenant_id, code)
            if existing:
                raise ValidationAPIException(f"Clinic with code '{code}' already exists for this tenant")
            
            clinic = TenantClinic(
                tenant_id=tenant_id,
                code=code,
                name=name,
                description=description,
                address=address,
                phone=phone,
                email=email,
                is_active=is_active,
            )
            
            self.db.add(clinic)
            await self.db.commit()
            await self.db.refresh(clinic)
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="tenant_clinic",
                resource_id=clinic.id,
                action="create",
                after_snapshot=clinic.__dict__,
                request_context=request_context,
            )
            
            logger.info(f"Created clinic {clinic.id} for tenant {tenant_id}")
            
            return clinic
            
        except ValidationAPIException:
            raise
        except Exception as e:
            logger.error(f"Error creating clinic: {e}")
            raise ValidationAPIException(f"Failed to create clinic: {str(e)}")
    
    async def get_clinic_by_id(self, tenant_id: UUID, clinic_id: int) -> Optional[TenantClinic]:
        """Get clinic by ID for a specific tenant."""
        result = await self.db.execute(
            select(TenantClinic).where(
                and_(
                    TenantClinic.id == clinic_id,
                    TenantClinic.tenant_id == tenant_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_clinic_by_code(self, tenant_id: UUID, code: str) -> Optional[TenantClinic]:
        """Get clinic by code for a specific tenant."""
        result = await self.db.execute(
            select(TenantClinic).where(
                and_(
                    TenantClinic.code == code,
                    TenantClinic.tenant_id == tenant_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_clinics(self, tenant_id: UUID, active_only: bool = True) -> List[TenantClinic]:
        """Get all clinics for a tenant."""
        query = select(TenantClinic).where(TenantClinic.tenant_id == tenant_id)
        
        if active_only:
            query = query.where(TenantClinic.is_active == "true")
        
        query = query.order_by(TenantClinic.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_clinic(
        self,
        tenant_id: UUID,
        clinic_id: int,
        request_context: Optional[dict] = None,
        **updates: any,
    ) -> Optional[TenantClinic]:
        """Update a clinic."""
        
        clinic = await self.get_clinic_by_id(tenant_id, clinic_id)
        if not clinic:
            raise NotFoundAPIException("Clinic not found")
        
        try:
            # Check if code is being updated and if it already exists
            if "code" in updates and updates["code"] != clinic.code:
                existing = await self.get_clinic_by_code(tenant_id, updates["code"])
                if existing:
                    raise ValidationAPIException(f"Clinic with code '{updates['code']}' already exists for this tenant")
            
            # Store before snapshot for audit
            before_snapshot = clinic.__dict__.copy()
            
            # Update fields
            for field, value in updates.items():
                if hasattr(clinic, field) and value is not None:
                    setattr(clinic, field, value)
            
            await self.db.commit()
            await self.db.refresh(clinic)
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="tenant_clinic",
                resource_id=clinic.id,
                action="update",
                before_snapshot=before_snapshot,
                after_snapshot=clinic.__dict__,
                request_context=request_context,
            )
            
            logger.info(f"Updated clinic {clinic.id} for tenant {tenant_id}")
            
            return clinic
            
        except ValidationAPIException:
            raise
        except Exception as e:
            logger.error(f"Error updating clinic: {e}")
            raise ValidationAPIException(f"Failed to update clinic: {str(e)}")
    
    async def delete_clinic(
        self,
        tenant_id: UUID,
        clinic_id: int,
        request_context: Optional[dict] = None,
    ) -> bool:
        """Delete a clinic (soft delete by setting is_active to false)."""
        
        clinic = await self.get_clinic_by_id(tenant_id, clinic_id)
        if not clinic:
            raise NotFoundAPIException("Clinic not found")
        
        try:
            # Soft delete by setting is_active to false
            clinic.is_active = "false"
            await self.db.commit()
            
            # Log audit trail
            await self.audit_service.log_action_with_context(
                resource_type="tenant_clinic",
                resource_id=clinic.id,
                action="delete",
                after_snapshot=clinic.__dict__,
                request_context=request_context,
            )
            
            logger.info(f"Deleted clinic {clinic.id} for tenant {tenant_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting clinic: {e}")
            raise ValidationAPIException(f"Failed to delete clinic: {str(e)}")
