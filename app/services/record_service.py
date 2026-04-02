"""
Financial record service — business logic for record CRUD and filtering.

Validates inputs, coordinates with the repository layer, and formats
responses for the router.
"""

from sqlalchemy.orm import Session

from app.models.record import FinancialRecord, RecordType
from app.models.user import User
from app.repositories.record_repository import RecordRepository
from app.schemas.record import CreateRecordRequest, UpdateRecordRequest
from app.utils.exceptions import NotFoundException


class RecordService:
    """Handles financial record operations."""

    def __init__(self, db: Session):
        self.record_repo = RecordRepository(db)

    def create_record(self, data: CreateRecordRequest, user: User) -> dict:
        """Create a new financial record.

        The record is automatically associated with the creating user
        for audit trail purposes.
        """
        record = FinancialRecord(
            amount=float(data.amount),
            type=RecordType(data.record_type),
            category=data.category.strip(),
            date=data.record_date,
            description=data.description.strip() if data.description else None,
            user_id=user.id,
        )
        record = self.record_repo.create(record)
        return _record_to_dict(record)

    def list_records(
        self,
        page: int = 1,
        limit: int = 20,
        record_type: str | None = None,
        category: str | None = None,
        start_date=None,
        end_date=None,
        search: str | None = None,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> tuple[list[dict], int]:
        """List records with filtering, search, sorting, and pagination.

        Returns:
            Tuple of (record_dicts, total_count).
        """
        records, total = self.record_repo.find_all(
            page=page,
            limit=limit,
            record_type=record_type,
            category=category,
            start_date=start_date,
            end_date=end_date,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [_record_to_dict(r) for r in records], total

    def get_record(self, record_id: str) -> dict:
        """Get a single record by ID.

        Raises:
            NotFoundException: If record not found or soft-deleted.
        """
        record = self.record_repo.find_by_id(record_id)
        if not record:
            raise NotFoundException("Financial record", record_id)
        return _record_to_dict(record)

    def update_record(self, record_id: str, data: UpdateRecordRequest) -> dict:
        """Update a record (PATCH semantics).

        Only provided (non-None) fields are updated.

        Raises:
            NotFoundException: If record not found.
        """
        record = self.record_repo.find_by_id(record_id)
        if not record:
            raise NotFoundException("Financial record", record_id)

        if data.amount is not None:
            record.amount = float(data.amount)
        if data.record_type is not None:
            record.type = RecordType(data.record_type)
        if data.category is not None:
            record.category = data.category.strip()
        if data.record_date is not None:
            record.date = data.record_date
        if data.description is not None:
            record.description = data.description.strip() if data.description else None

        record = self.record_repo.update(record)
        return _record_to_dict(record)

    def delete_record(self, record_id: str) -> dict:
        """Soft-delete a record.

        Raises:
            NotFoundException: If record not found.
        """
        record = self.record_repo.find_by_id(record_id)
        if not record:
            raise NotFoundException("Financial record", record_id)

        self.record_repo.soft_delete(record)
        return {"message": f"Financial record '{record_id}' has been deleted"}


def _record_to_dict(record: FinancialRecord) -> dict:
    """Convert a FinancialRecord model to a response dict."""
    return {
        "id": record.id,
        "amount": float(record.amount),
        "type": record.type.value,
        "category": record.category,
        "date": str(record.date),
        "description": record.description,
        "user_id": record.user_id,
        "created_at": str(record.created_at),
        "updated_at": str(record.updated_at),
    }
