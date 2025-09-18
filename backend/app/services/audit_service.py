"""Audit service for tracking changes."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for managing audit logs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_action(
        self,
        tenant_id: UUID,
        resource_type: str,
        resource_id: UUID,
        action: str,
        api_key_id: Optional[UUID] = None,
        before_snapshot: Optional[Dict[str, Any]] = None,
        after_snapshot: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log an action for audit purposes."""
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            api_key_id=api_key_id,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        
        logger.debug(f"Logged {action} action for {resource_type}:{resource_id}")
        
        return audit_log
    
    async def get_audit_logs_by_resource(
        self,
        resource_type: str,
        resource_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Get audit logs for a specific resource."""
        
        query = select(AuditLog).where(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_audit_logs_by_tenant(
        self,
        tenant_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Get audit logs for a tenant."""
        
        query = select(AuditLog).where(
            AuditLog.tenant_id == tenant_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_audit_logs_by_action(
        self,
        action: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Get audit logs by action type."""
        
        query = select(AuditLog).where(
            AuditLog.action == action
        ).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def log_action_with_context(
        self,
        resource_type: str,
        resource_id: UUID,
        action: str,
        before_snapshot: Optional[Dict[str, Any]] = None,
        after_snapshot: Optional[Dict[str, Any]] = None,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Log an action with automatic request context extraction."""
        
        if not request_context:
            request_context = {}
        
        return await self.log_action(
            tenant_id=request_context.get("tenant_id"),
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            api_key_id=request_context.get("api_key_id"),
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            request_id=request_context.get("request_id"),
            ip_address=request_context.get("ip_address"),
            user_agent=request_context.get("user_agent"),
        )