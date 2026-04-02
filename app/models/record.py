"""
Financial Record model.

Represents a single financial entry (income or expense) in the system.
Uses Decimal (Numeric) for amount to avoid floating-point precision errors —
critical for any financial application.
"""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecordType(str, enum.Enum):
    """Type of financial record."""
    INCOME = "income"
    EXPENSE = "expense"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False  # Up to 9,999,999,999.99
    )
    type: Mapped[RecordType] = mapped_column(
        Enum(RecordType), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    # Foreign key to creator
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    created_by_user = relationship("User", back_populates="records")

    def __repr__(self) -> str:
        return f"<FinancialRecord {self.type.value} {self.amount} {self.category}>"
