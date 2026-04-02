"""
User repository — data access layer.

All SQLAlchemy queries for User live here. No business logic.
This makes the service layer testable without a real database.
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus


class UserRepository:
    """Encapsulates all database operations for the User model."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, user_id: str) -> User | None:
        """Find a non-deleted user by ID."""
        return (
            self.db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )

    def find_by_email(self, email: str) -> User | None:
        """Find a non-deleted user by email."""
        return (
            self.db.query(User)
            .filter(User.email == email, User.deleted_at.is_(None))
            .first()
        )

    def find_all(
        self,
        page: int = 1,
        limit: int = 20,
        role: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        """Find all non-deleted users with optional filtering and pagination.

        Returns:
            Tuple of (users_list, total_count).
        """
        query = self.db.query(User).filter(User.deleted_at.is_(None))

        # Apply filters
        if role:
            query = query.filter(User.role == UserRole(role))
        if status:
            query = query.filter(User.status == UserStatus(status))
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                )
            )

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

        return users, total

    def create(self, user: User) -> User:
        """Insert a new user into the database."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Commit changes to an existing user."""
        self.db.commit()
        self.db.refresh(user)
        return user

    def soft_delete(self, user: User) -> User:
        """Soft-delete a user by setting deleted_at."""
        from datetime import datetime, timezone
        user.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user
