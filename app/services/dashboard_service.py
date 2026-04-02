"""
Dashboard service — business logic for analytics and summary data.

Thin wrapper over DashboardRepository — most of the heavy lifting is
in the SQL queries. This layer exists for consistency and for any
future business rules (e.g., filtering by date range, user-specific dashboards).
"""

from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    """Handles dashboard analytics operations."""

    def __init__(self, db: Session):
        self.dashboard_repo = DashboardRepository(db)

    def get_summary(self) -> dict:
        """Get overall financial summary.

        Returns total income, expenses, net balance, and record count.
        """
        return self.dashboard_repo.get_summary()

    def get_category_breakdown(self) -> list[dict]:
        """Get income/expense breakdown by category.

        Returns category-wise totals sorted by volume.
        """
        return self.dashboard_repo.get_category_breakdown()

    def get_monthly_trends(self, months: int = 12) -> list[dict]:
        """Get monthly income/expense trends.

        Returns chronologically ordered monthly aggregates.
        """
        return self.dashboard_repo.get_monthly_trends(months=months)

    def get_recent_activity(self, limit: int = 10) -> list[dict]:
        """Get the most recent financial records.

        Returns the latest N records for the activity feed.
        """
        records = self.dashboard_repo.get_recent_activity(limit=limit)
        return [
            {
                "id": r.id,
                "amount": float(r.amount),
                "type": r.type.value,
                "category": r.category,
                "date": str(r.date),
                "description": r.description,
                "created_at": str(r.created_at),
            }
            for r in records
        ]
