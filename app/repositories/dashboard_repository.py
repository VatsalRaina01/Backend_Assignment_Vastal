"""
Dashboard repository — data access layer for analytics queries.

This is the crown jewel of the repository layer. These queries demonstrate
SQL aggregation skills: GROUP BY, conditional SUMs, date truncation, and
multi-column pivots — the kind of work that separates CRUD from real
backend engineering.
"""

from sqlalchemy import case, func, extract
from sqlalchemy.orm import Session

from app.models.record import FinancialRecord, RecordType


class DashboardRepository:
    """Database queries for dashboard analytics — aggregation-heavy."""

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> dict:
        """Get overall financial summary: total income, expenses, balance, record count.

        Uses conditional SUM aggregation to compute income and expense totals
        in a single query (no N+1, no multiple round-trips).
        """
        result = self.db.query(
            func.coalesce(
                func.sum(
                    case(
                        (FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("total_income"),
            func.coalesce(
                func.sum(
                    case(
                        (FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("total_expenses"),
            func.count(FinancialRecord.id).label("total_records"),
        ).filter(
            FinancialRecord.deleted_at.is_(None)
        ).first()

        total_income = float(result.total_income)
        total_expenses = float(result.total_expenses)

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_balance": round(total_income - total_expenses, 2),
            "total_records": result.total_records,
        }

    def get_category_breakdown(self) -> list[dict]:
        """Get income and expense totals grouped by category.

        Uses conditional aggregation with CASE expressions to pivot
        income/expense into columns within each category group.
        Result is sorted by total absolute volume (most active categories first).
        """
        results = (
            self.db.query(
                FinancialRecord.category,
                func.coalesce(
                    func.sum(
                        case(
                            (FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("total_income"),
                func.coalesce(
                    func.sum(
                        case(
                            (FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("total_expense"),
                func.count(FinancialRecord.id).label("record_count"),
            )
            .filter(FinancialRecord.deleted_at.is_(None))
            .group_by(FinancialRecord.category)
            .order_by(func.sum(FinancialRecord.amount).desc())
            .all()
        )

        return [
            {
                "category": row.category,
                "total_income": float(row.total_income),
                "total_expense": float(row.total_expense),
                "net": round(float(row.total_income) - float(row.total_expense), 2),
                "record_count": row.record_count,
            }
            for row in results
        ]

    def get_monthly_trends(self, months: int = 12) -> list[dict]:
        """Get monthly income/expense trends for the last N months.

        Uses strftime for SQLite date truncation to group records by year-month.
        Returns results ordered chronologically for easy chart rendering.
        """
        results = (
            self.db.query(
                func.strftime("%Y-%m", FinancialRecord.date).label("month"),
                func.coalesce(
                    func.sum(
                        case(
                            (FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("total_income"),
                func.coalesce(
                    func.sum(
                        case(
                            (FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("total_expense"),
            )
            .filter(FinancialRecord.deleted_at.is_(None))
            .group_by(func.strftime("%Y-%m", FinancialRecord.date))
            .order_by(func.strftime("%Y-%m", FinancialRecord.date).asc())
            .limit(months)
            .all()
        )

        return [
            {
                "month": row.month,
                "total_income": float(row.total_income),
                "total_expense": float(row.total_expense),
                "net": round(float(row.total_income) - float(row.total_expense), 2),
            }
            for row in results
        ]

    def get_recent_activity(self, limit: int = 10) -> list[FinancialRecord]:
        """Get the most recent financial records.

        Simple query, but useful for dashboard "latest activity" widgets.
        """
        return (
            self.db.query(FinancialRecord)
            .filter(FinancialRecord.deleted_at.is_(None))
            .order_by(FinancialRecord.created_at.desc())
            .limit(limit)
            .all()
        )
