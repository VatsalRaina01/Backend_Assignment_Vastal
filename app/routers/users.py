"""
Users router — admin-only user management endpoints.

All endpoints require admin role. Uses RoleChecker dependency
for clean, declarative access control.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import allow_admin_only, get_db
from app.models.user import User
from app.schemas.user import UpdateUserRequest
from app.services.user_service import UserService
from app.utils.response import paginated_response, success_response

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])


@router.get("", summary="List all users (Admin only)")
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_admin_only),
):
    """List all users with optional filtering and pagination.

    **Access**: Admin only
    """
    service = UserService(db)
    users, total = service.list_users(
        page=page, limit=limit, role=role, status=status, search=search
    )
    return paginated_response(data=users, total=total, page=page, limit=limit)


@router.get("/{user_id}", summary="Get user by ID (Admin only)")
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_admin_only),
):
    """Get details of a specific user.

    **Access**: Admin only
    """
    service = UserService(db)
    user = service.get_user(user_id)
    return success_response(data=user)


@router.patch("/{user_id}", summary="Update user (Admin only)")
def update_user(
    user_id: str,
    data: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_admin_only),
):
    """Update user details (PATCH semantics — only send fields to change).

    **Access**: Admin only
    
    Updatable fields: `name`, `email`, `role`, `status`
    """
    service = UserService(db)
    user = service.update_user(user_id, data)
    return success_response(data=user, message="User updated successfully")


@router.delete("/{user_id}", summary="Delete user (Admin only)")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_admin_only),
):
    """Soft-delete a user (sets deleted_at, does not remove from DB).

    **Access**: Admin only
    
    - You cannot delete your own account.
    - Deleted users can no longer log in.
    """
    service = UserService(db)
    result = service.delete_user(user_id, current_user)
    return success_response(data=result, message="User deleted successfully")
