"""
User management service — business logic for admin user operations.

Handles listing, updating, and soft-deleting users with proper
validation and access control enforcement.
"""

from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.user import UpdateUserRequest
from app.utils.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)


class UserService:
    """Handles user management operations (admin only)."""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def list_users(
        self,
        page: int = 1,
        limit: int = 20,
        role: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[dict], int]:
        """List all users with filtering and pagination.

        Returns:
            Tuple of (user_dicts, total_count).
        """
        users, total = self.user_repo.find_all(
            page=page, limit=limit, role=role, status=status, search=search
        )
        return [_user_to_dict(u) for u in users], total

    def get_user(self, user_id: str) -> dict:
        """Get a single user by ID.

        Raises:
            NotFoundException: If user not found.
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return _user_to_dict(user)

    def update_user(self, user_id: str, data: UpdateUserRequest) -> dict:
        """Update user fields (PATCH semantics — only set provided fields).

        Business rules:
        - Only provided (non-None) fields are updated
        - Email must remain unique if changed
        - Role and status must be valid enum values

        Raises:
            NotFoundException: If user not found.
            ConflictException: If new email already exists.
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        # Update only provided fields
        if data.name is not None:
            user.name = data.name

        if data.email is not None:
            existing = self.user_repo.find_by_email(data.email)
            if existing and existing.id != user_id:
                raise ConflictException(f"Email '{data.email}' is already in use")
            user.email = data.email

        if data.role is not None:
            user.role = UserRole(data.role)

        if data.status is not None:
            user.status = UserStatus(data.status)

        user = self.user_repo.update(user)
        return _user_to_dict(user)

    def delete_user(self, user_id: str, current_user: User) -> dict:
        """Soft-delete a user.

        Business rules:
        - Cannot delete yourself (prevents admin lockout)
        - Sets deleted_at timestamp instead of hard delete

        Raises:
            NotFoundException: If user not found.
            BadRequestException: If trying to self-delete.
        """
        if user_id == current_user.id:
            raise BadRequestException("You cannot delete your own account")

        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        self.user_repo.soft_delete(user)
        return {"message": f"User '{user.email}' has been deactivated"}


def _user_to_dict(user: User) -> dict:
    """Convert a User model to a safe dict (no password)."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "status": user.status.value,
        "created_at": str(user.created_at),
        "updated_at": str(user.updated_at),
    }
