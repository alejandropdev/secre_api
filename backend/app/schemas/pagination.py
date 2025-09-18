"""Pagination Pydantic schemas."""

from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(50, ge=1, le=100, description="Page size (1-100)")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic schema for paginated responses."""
    
    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    total_pages: int = Field(..., description="Total number of pages")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        total_pages = (total + size - 1) // size
        has_next = page < total_pages
        has_prev = page > 1
        
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            has_next=has_next,
            has_prev=has_prev,
            total_pages=total_pages,
        )
