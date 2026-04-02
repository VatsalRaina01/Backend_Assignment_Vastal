"""
Financial record repository — data access layer.

Handles all database queries for FinancialRecord including
filtered listing, CRUD, and count operations.
"""

from datetime import date

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.record import FinancialRecord, RecordType


class RecordRepository:
    """Encapsulates all database operations for the FinancialRecord model."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, record_id: str) -> FinancialRecord | None:
        """Find a non-deleted record by ID."""
        return (
            self.db.query(FinancialRecord)
            .filter(
                FinancialRecord.id == record_id,
                FinancialRecord.deleted_at.is_(None),
            )
            .first()
        )

    def find_all(
        self,
        page: int = 1,
        limit: int = 20,
        record_type: str | None = None,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search: str | None = None,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> tuple[list[FinancialRecord], int]:
        """Find all non-deleted records with filtering, search, and pagination.

        Returns:
            Tuple of (records_list, total_count).
        """
        query = self.db.query(FinancialRecord).filter(
            FinancialRecord.deleted_at.is_(None)
        )

        # ── Apply filters ────────────────────────────────────────────
        if record_type:
            query = query.filter(FinancialRecord.type == RecordType(record_type))
        if category:
            query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))
        if start_date:
            query = query.filter(FinancialRecord.date >= start_date)
        if end_date:
            query = query.filter(FinancialRecord.date <= end_date)
        if search:
            query = query.filter(
                FinancialRecord.description.ilike(f"%{search}%")
            )

        # ── Total count before pagination ────────────────────────────
        total = query.count()

        # ── Sorting ──────────────────────────────────────────────────
        sort_column_map = {
            "date": FinancialRecord.date,
            "amount": FinancialRecord.amount,
            "created_at": FinancialRecord.created_at,
            "category": FinancialRecord.category,
        }
        sort_col = sort_column_map.get(sort_by, FinancialRecord.date)
        order_func = desc if sort_order == "desc" else asc
        query = query.order_by(order_func(sort_col))

        # ── Pagination ───────────────────────────────────────────────
        offset = (page - 1) * limit
        records = query.offset(offset).limit(limit).all()

        return records, total

    def create(self, record: FinancialRecord) -> FinancialRecord:
        """Insert a new financial record."""
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: FinancialRecord) -> FinancialRecord:
        """Commit changes to an existing record."""
        self.db.commit()
        self.db.refresh(record)
        return record

    def soft_delete(self, record: FinancialRecord) -> FinancialRecord:
        """Soft-delete a record by setting deleted_at."""
        from datetime import datetime, timezone
        record.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(record)
        return record
