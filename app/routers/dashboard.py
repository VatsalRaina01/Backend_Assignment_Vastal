"""
Dashboard router — analytics and summary endpoints.

Access control: Analyst and Admin only.
Viewers can see individual records but cannot access aggregated insights.
This is a deliberate design choice to demonstrate granular RBAC.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import allow_analyst_admin, get_db
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard Analytics"])


@router.get("/summary", summary="Get financial summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_analyst_admin),
):
    """Get overall financial summary.

    **Access**: Analyst, Admin

    Returns:
    - Total income across all records
    - Total expenses across all records
    - Net balance (income - expenses)
    - Total number of active records
    """
    service = DashboardService(db)
    summary = service.get_summary()
    return success_response(data=summary, message="Summary retrieved")


@router.get("/category-breakdown", summary="Get category-wise breakdown")
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_analyst_admin),
):
    """Get income and expense totals grouped by category.

    **Access**: Analyst, Admin

    Categories are sorted by total financial volume (most active first).
    Each category includes:
    - Total income
    - Total expense
    - Net (income - expense)
    - Number of records
    """
    service = DashboardService(db)
    breakdown = service.get_category_breakdown()
    return success_response(data=breakdown, message="Category breakdown retrieved")


@router.get("/trends", summary="Get monthly trends")
def get_monthly_trends(
    months: int = Query(12, ge=1, le=60, description="Number of months to include"),
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_analyst_admin),
):
    """Get monthly income/expense trends.

    **Access**: Analyst, Admin

    Returns chronologically ordered monthly aggregates for chart rendering.
    Each month includes total income, total expense, and net balance.
    """
    service = DashboardService(db)
    trends = service.get_monthly_trends(months=months)
    return success_response(data=trends, message="Monthly trends retrieved")


@router.get("/recent-activity", summary="Get recent activity")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Number of recent records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_analyst_admin),
):
    """Get the most recent financial records.

    **Access**: Analyst, Admin

    Returns the latest N records ordered by creation date,
    useful for a dashboard activity feed.
    """
    service = DashboardService(db)
    activity = service.get_recent_activity(limit=limit)
    return success_response(data=activity, message="Recent activity retrieved")
