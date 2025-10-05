"""API Key Usage Statistics Pydantic schemas."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class EndpointUsageStatsSchema(BaseSchema):
    """Schema for endpoint usage statistics."""
    
    endpoint: str = Field(..., description="API endpoint path")
    method: str = Field(..., description="HTTP method")
    total_requests: int = Field(..., description="Total number of requests")
    avg_response_time_ms: float = Field(..., description="Average response time in milliseconds")


class StatusCodeStatsSchema(BaseSchema):
    """Schema for status code statistics."""
    
    status_code: int = Field(..., description="HTTP status code")
    total_requests: int = Field(..., description="Total number of requests")


class DailyUsageSchema(BaseSchema):
    """Schema for daily usage data."""
    
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_requests: int = Field(..., description="Total requests on this date")


class HourlyUsageSchema(BaseSchema):
    """Schema for hourly usage data."""
    
    hour: int = Field(..., description="Hour of day (0-23)")
    total_requests: int = Field(..., description="Total requests in this hour")


class ApiKeyUsageStatsSchema(BaseSchema):
    """Schema for comprehensive API key usage statistics."""
    
    api_key_id: str = Field(..., description="API key ID")
    period_days: int = Field(..., description="Number of days in the period")
    start_date: str = Field(..., description="Start date of the period")
    end_date: str = Field(..., description="End date of the period")
    total_requests: int = Field(..., description="Total requests in the period")
    endpoint_stats: List[EndpointUsageStatsSchema] = Field(..., description="Usage by endpoint")
    status_stats: List[StatusCodeStatsSchema] = Field(..., description="Usage by status code")
    daily_usage: List[DailyUsageSchema] = Field(..., description="Daily usage breakdown")
    hourly_usage: List[HourlyUsageSchema] = Field(..., description="Hourly usage breakdown")


class ApiKeyStatsSchema(BaseSchema):
    """Schema for API key statistics within tenant."""
    
    api_key_id: str = Field(..., description="API key ID")
    total_requests: int = Field(..., description="Total requests")
    avg_response_time_ms: float = Field(..., description="Average response time in milliseconds")


class TenantUsageStatsSchema(BaseSchema):
    """Schema for tenant usage statistics."""
    
    tenant_id: str = Field(..., description="Tenant ID")
    period_days: int = Field(..., description="Number of days in the period")
    start_date: str = Field(..., description="Start date of the period")
    end_date: str = Field(..., description="End date of the period")
    total_requests: int = Field(..., description="Total requests for the tenant")
    api_key_stats: List[ApiKeyStatsSchema] = Field(..., description="Usage by API key")


class TopEndpointsSchema(BaseSchema):
    """Schema for top endpoints by usage."""
    
    endpoint: str = Field(..., description="API endpoint path")
    method: str = Field(..., description="HTTP method")
    total_requests: int = Field(..., description="Total number of requests")
    avg_response_time_ms: float = Field(..., description="Average response time in milliseconds")


class UsageStatsResponseSchema(BaseSchema):
    """Schema for usage statistics response."""
    
    stats: ApiKeyUsageStatsSchema = Field(..., description="Usage statistics")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the stats were generated")


class TenantUsageStatsResponseSchema(BaseSchema):
    """Schema for tenant usage statistics response."""
    
    stats: TenantUsageStatsSchema = Field(..., description="Tenant usage statistics")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the stats were generated")


class TopEndpointsResponseSchema(BaseSchema):
    """Schema for top endpoints response."""
    
    endpoints: List[TopEndpointsSchema] = Field(..., description="Top endpoints by usage")
    period_days: int = Field(..., description="Number of days in the period")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the stats were generated")
