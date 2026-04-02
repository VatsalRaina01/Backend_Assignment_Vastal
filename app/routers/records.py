"""
Financial records router — CRUD with filtering, search, and pagination.

Access control:
- GET (list/detail): Any authenticated role (viewer, analyst, admin)
- POST/PATCH/DELETE: Admin only
"""

from datetime import date as date_type
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import allow_admin_only, allow_any_authenticated, get_db
from app.models.user import User
from app.schemas.record import CreateRecordRequest, UpdateRecordRequest
from app.services.record_service import RecordService
from app.utils.response import paginated_response, success_response

router = APIRouter(prefix="/api/v1/records", tags=["Financial Records"])


@router.post("", status_code=201, summary="Create a financial record (Admin only)")
def create_record(
    data: CreateRecordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_admin_only),
):
    """Create a new financial record (income or expense).

    **Access**: Admin only

    The record is automatically associated with the creating user for audit purposes.
    """
    service = RecordService(db)
    record = service.create_record(data, current_user)
    return success_response(data=record, message="Record created successfully")


@router.get("", summary="List financial records")
def list_records(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    record_type: Optional[str] = Query(None, alias="type", description="Filter: income or expense"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[date_type] = Query(None, description="Filter: start date (YYYY-MM-DD)"),
    end_date: Optional[date_type] = Query(None, description="Filter: end date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in description"),
    sort_by: str = Query("date", description="Sort by: date, amount, created_at, category"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_any_authenticated),
):
    """List all financial records with optional filtering and pagination.

    **Access**: All authenticated users (viewer, analyst, admin)

    **Filters**: type, category, date range, search text  
    **Sorting**: date (default), amount, created_at, category  
    **Pagination**: page + limit (max 100 per page)
    """
    service = RecordService(db)
    records, total = service.list_records(
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
    return paginated_response(data=records, total=total, page=page, limit=limit)


@router.get("/{record_id}", summary="Get a financial record")
def get_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_any_authenticated),
):
    """Get details of a specific financial record.

    **Access**: All authenticated users
    """
    service = RecordService(db)
    record = service.get_record(record_id)
    return success_response(data=record)


@router.patch("/{record_id}", summary="Update a financial record (Admin only)")
def update_record(
    record_id: str,
    data: UpdateRecordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_admin_only),
):
    """Update a financial record (PATCH semantics — only send fields to change).

    **Access**: Admin only
    """
    service = RecordService(db)
    record = service.update_record(record_id, data)
    return success_response(data=record, message="Record updated successfully")


@router.delete("/{record_id}", summary="Delete a financial record (Admin only)")
def delete_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_admin_only),
):
    """Soft-delete a financial record.

    **Access**: Admin only

    The record is not permanently removed — it is marked with a
    `deleted_at` timestamp and excluded from all queries.
    """
    service = RecordService(db)
    result = service.delete_record(record_id)
    return success_response(data=result, message="Record deleted successfully")
