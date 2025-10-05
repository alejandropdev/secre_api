"""API Key Usage service for tracking and analyzing API usage metrics."""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key_usage import ApiKeyUsage

logger = logging.getLogger(__name__)


class ApiKeyUsageService:
    """Service for managing API key usage metrics."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def track_request(
        self,
        api_key_id: UUID,
        tenant_id: UUID,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Track a single API request."""
        
        usage_date = date.today()
        usage_hour = datetime.now().hour
        
        # Check if we already have a record for this combination today
        existing_record = await self._get_existing_record(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            usage_date=usage_date,
            usage_hour=usage_hour,
        )
        
        if existing_record:
            # Increment the request count
            existing_record.request_count += 1
            if response_time_ms:
                # Update average response time
                existing_record.response_time_ms = (
                    (existing_record.response_time_ms or 0) + response_time_ms
                ) // 2
        else:
            # Create new record
            usage_record = ApiKeyUsage(
                api_key_id=api_key_id,
                tenant_id=tenant_id,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                request_count=1,
                response_time_ms=response_time_ms,
                usage_date=usage_date,
                usage_hour=usage_hour,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.add(usage_record)
        
        await self.db.commit()
    
    async def _get_existing_record(
        self,
        api_key_id: UUID,
        endpoint: str,
        method: str,
        status_code: int,
        usage_date: date,
        usage_hour: int,
    ) -> Optional[ApiKeyUsage]:
        """Get existing usage record for the same parameters."""
        
        result = await self.db.execute(
            select(ApiKeyUsage)
            .where(
                and_(
                    ApiKeyUsage.api_key_id == api_key_id,
                    ApiKeyUsage.endpoint == endpoint,
                    ApiKeyUsage.method == method,
                    ApiKeyUsage.status_code == status_code,
                    ApiKeyUsage.usage_date == usage_date,
                    ApiKeyUsage.usage_hour == usage_hour,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_api_key_usage_stats(
        self,
        api_key_id: UUID,
        days: int = 30,
    ) -> Dict:
        """Get comprehensive usage statistics for an API key."""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get total requests
        total_requests_result = await self.db.execute(
            select(func.sum(ApiKeyUsage.request_count))
            .where(
                and_(
                    ApiKeyUsage.api_key_id == api_key_id,
                    ApiKeyUsage.usage_date >= start_date,
                    ApiKeyUsage.usage_date <= end_date,
                )
            )
        )
        total_requests = total_requests_result.scalar() or 0
        
        # Get requests by endpoint
        endpoint_stats_result = await self.db.execute(
            select(
                ApiKeyUsage.endpoint,
                ApiKeyUsage.method,
                func.sum(ApiKeyUsage.request_count).label('total_requests'),
                func.avg(ApiKeyUsage.response_time_ms).label('avg_response_time'),
            )
            .where(
                and_(
                    ApiKeyUsage.api_key_id == api_key_id,
                    ApiKeyUsage.usage_date >= start_date,
                    ApiKeyUsage.usage_date <= end_date,
                )
            )
            .group_by(ApiKeyUsage.endpoint, ApiKeyUsage.method)
            .order_by(desc('total_requests'))
        )
        endpoint_stats = [
            {
                'endpoint': row.endpoint,
                'method': row.method,
                'total_requests': row.total_requests,
                'avg_response_time_ms': round(row.avg_response_time or 0, 2),
            }
            for row in endpoint_stats_result
        ]
        
        # Get requests by status code
        status_stats_result = await self.db.execute(
            select(
                ApiKeyUsage.status_code,
                func.sum(ApiKeyUsage.request_count).label('total_requests'),
            )
            .where(
                and_(
                    ApiKeyUsage.api_key_id == api_key_id,
                    ApiKeyUsage.usage_date >= start_date,
                    ApiKeyUsage.usage_date <= end_date,
                )
            )
            .group_by(ApiKeyUsage.status_code)
            .order_by(desc('total_requests'))
        )
        status_stats = [
            {
                'status_code': row.status_code,
                'total_requests': row.total_requests,
            }
            for row in status_stats_result
        ]
        
        # Get daily usage
        daily_usage_result = await self.db.execute(
            select(
                ApiKeyUsage.usage_date,
                func.sum(ApiKeyUsage.request_count).label('total_requests'),
            )
            .where(
                and_(
                    ApiKeyUsage.api_key_id == api_key_id,
                    ApiKeyUsage.usage_date >= start_date,
                    ApiKeyUsage.usage_date <= end_date,
                )
            )
            .group_by(ApiKeyUsage.usage_date)
            .order_by(ApiKeyUsage.usage_date)
        )
        daily_usage = [
            {
                'date': row.usage_date.isoformat(),
                'total_requests': row.total_requests,
            }
            for row in daily_usage_result
        ]
        
        # Get hourly usage (last 7 days)
        hourly_start_date = end_date - timedelta(days=7)
        hourly_usage_result = await self.db.execute(
            select(
                ApiKeyUsage.usage_hour,
                func.sum(ApiKeyUsage.request_count).label('total_requests'),
            )
            .where(
                and_(
                    ApiKeyUsage.api_key_id == api_key_id,
                    ApiKeyUsage.usage_date >= hourly_start_date,
                    ApiKeyUsage.usage_date <= end_date,
                )
            )
            .group_by(ApiKeyUsage.usage_hour)
            .order_by(ApiKeyUsage.usage_hour)
        )
        hourly_usage = [
            {
                'hour': row.usage_hour,
                'total_requests': row.total_requests,
            }
            for row in hourly_usage_result
        ]
        
        return {
            'api_key_id': str(api_key_id),
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_requests': total_requests,
            'endpoint_stats': endpoint_stats,
            'status_stats': status_stats,
            'daily_usage': daily_usage,
            'hourly_usage': hourly_usage,
        }
    
    async def get_tenant_usage_stats(
        self,
        tenant_id: UUID,
        days: int = 30,
    ) -> Dict:
        """Get usage statistics for all API keys in a tenant."""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get total requests for tenant
        total_requests_result = await self.db.execute(
            select(func.sum(ApiKeyUsage.request_count))
            .where(
                and_(
                    ApiKeyUsage.tenant_id == tenant_id,
                    ApiKeyUsage.usage_date >= start_date,
                    ApiKeyUsage.usage_date <= end_date,
                )
            )
        )
        total_requests = total_requests_result.scalar() or 0
        
        # Get usage by API key
        api_key_stats_result = await self.db.execute(
            select(
                ApiKeyUsage.api_key_id,
                func.sum(ApiKeyUsage.request_count).label('total_requests'),
                func.avg(ApiKeyUsage.response_time_ms).label('avg_response_time'),
            )
            .where(
                and_(
                    ApiKeyUsage.tenant_id == tenant_id,
                    ApiKeyUsage.usage_date >= start_date,
                    ApiKeyUsage.usage_date <= end_date,
                )
            )
            .group_by(ApiKeyUsage.api_key_id)
            .order_by(desc('total_requests'))
        )
        api_key_stats = [
            {
                'api_key_id': str(row.api_key_id),
                'total_requests': row.total_requests,
                'avg_response_time_ms': round(row.avg_response_time or 0, 2),
            }
            for row in api_key_stats_result
        ]
        
        return {
            'tenant_id': str(tenant_id),
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_requests': total_requests,
            'api_key_stats': api_key_stats,
        }
    
    async def get_top_endpoints(
        self,
        tenant_id: Optional[UUID] = None,
        days: int = 7,
        limit: int = 10,
    ) -> List[Dict]:
        """Get top endpoints by usage across all tenants or specific tenant."""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = (
            select(
                ApiKeyUsage.endpoint,
                ApiKeyUsage.method,
                func.sum(ApiKeyUsage.request_count).label('total_requests'),
                func.avg(ApiKeyUsage.response_time_ms).label('avg_response_time'),
            )
            .where(
                and_(
                    ApiKeyUsage.usage_date >= start_date,
                    ApiKeyUsage.usage_date <= end_date,
                )
            )
            .group_by(ApiKeyUsage.endpoint, ApiKeyUsage.method)
            .order_by(desc('total_requests'))
            .limit(limit)
        )
        
        if tenant_id:
            query = query.where(ApiKeyUsage.tenant_id == tenant_id)
        
        result = await self.db.execute(query)
        
        return [
            {
                'endpoint': row.endpoint,
                'method': row.method,
                'total_requests': row.total_requests,
                'avg_response_time_ms': round(row.avg_response_time or 0, 2),
            }
            for row in result
        ]
    
    async def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """Clean up old usage records to prevent database bloat."""
        
        cutoff_date = date.today() - timedelta(days=days_to_keep)
        
        result = await self.db.execute(
            select(func.count(ApiKeyUsage.id))
            .where(ApiKeyUsage.usage_date < cutoff_date)
        )
        count_to_delete = result.scalar()
        
        if count_to_delete > 0:
            await self.db.execute(
                ApiKeyUsage.__table__.delete().where(
                    ApiKeyUsage.usage_date < cutoff_date
                )
            )
            await self.db.commit()
            logger.info(f"Cleaned up {count_to_delete} old usage records")
        
        return count_to_delete
