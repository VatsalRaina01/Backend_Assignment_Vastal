"""
Financial record Pydantic schemas for request/response validation.

Note: We use 'record_type' instead of 'type' as a field name to avoid
collision with Python 3.12+'s `type` soft keyword. The JSON API still
accepts/returns 'type' via Pydantic aliases.
"""

from __future__ import annotations

from datetime import date as date_type
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateRecordRequest(BaseModel):
    """Schema for creating a financial record."""
    amount: Decimal = Field(
        ..., gt=0, max_digits=12, decimal_places=2,
        description="Transaction amount (must be positive)"
    )
    record_type: Literal["income", "expense"] = Field(
        ..., alias="type", description="Record type"
    )
    category: str = Field(
        ..., min_length=1, max_length=100, description="Category name"
    )
    record_date: date_type = Field(
        ..., alias="date", description="Transaction date (YYYY-MM-DD)"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Optional description or notes"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "amount": 1500.00,
                "type": "income",
                "category": "Salary",
                "date": "2024-03-15",
                "description": "Monthly salary payment",
            }
        }
    )


class UpdateRecordRequest(BaseModel):
    """Schema for updating a financial record (PATCH semantics)."""
    amount: Optional[Decimal] = Field(
        None, gt=0, max_digits=12, decimal_places=2
    )
    record_type: Optional[Literal["income", "expense"]] = Field(
        None, alias="type"
    )
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    record_date: Optional[date_type] = Field(None, alias="date")
    description: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "amount": 2000.00,
                "category": "Freelance",
            }
        }
    )


class RecordResponse(BaseModel):
    """Schema for a financial record in API responses."""
    id: str
    amount: float
    record_type: str = Field(alias="type")
    category: str
    record_date: str = Field(alias="date")
    description: Optional[str] = None
    user_id: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RecordListParams(BaseModel):
    """Query parameters for listing / filtering records."""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    record_type: Optional[Literal["income", "expense"]] = Field(
        None, alias="type", description="Filter by type"
    )
    category: Optional[str] = Field(None, description="Filter by category")
    start_date: Optional[date_type] = Field(None, description="Start of date range")
    end_date: Optional[date_type] = Field(None, description="End of date range")
    search: Optional[str] = Field(
        None, description="Search in description (case-insensitive)"
    )
    sort_by: Literal["date", "amount", "created_at", "category"] = Field(
        "date", description="Sort field"
    )
    sort_order: Literal["asc", "desc"] = Field(
        "desc", description="Sort direction"
    )
