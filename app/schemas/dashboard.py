"""
Dashboard summary Pydantic schemas for response validation.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    """Overall financial summary."""
    total_income: float
    total_expenses: float
    net_balance: float
    total_records: int


class CategoryBreakdownItem(BaseModel):
    """Income/expense totals for a single category."""
    category: str
    total_income: float
    total_expense: float
    net: float
    record_count: int


class MonthlyTrendItem(BaseModel):
    """Income/expense totals for a single month."""
    month: str  # "2024-03"
    total_income: float
    total_expense: float
    net: float


class RecentActivityItem(BaseModel):
    """A recent financial record (simplified view)."""
    id: str
    amount: float
    record_type: str
    category: str
    record_date: str
    description: Optional[str] = None
    created_at: str
