"""
Authentication service — business logic for register, login, and profile.

Orchestrates between UserRepository, password hashing, and JWT creation.
"""

from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.exceptions import (
    ConflictException,
    UnauthorizedException,
    BadRequestException,
)
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import settings


class AuthService:
    """Handles user authentication flows."""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register(self, data: RegisterRequest) -> dict:
        """Register a new user.

        Business rules:
        - Email must be unique
        - Password is hashed with bcrypt before storage
        - New users default to 'viewer' role and 'active' status
        - Returns a JWT token immediately (register + auto-login)
        """
        # Check for existing user
        existing = self.user_repo.find_by_email(data.email)
        if existing:
            raise ConflictException(f"User with email '{data.email}' already exists")

        # Create user
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            name=data.name,
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
        )
        user = self.user_repo.create(user)

        # Generate token
        token = create_access_token(subject=user.id, role=user.role.value)

        return {
            "user": _user_to_dict(user),
            "token": {
                "access_token": token,
                "token_type": "bearer",
                "expires_in_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            },
        }

    def login(self, data: LoginRequest) -> dict:
        """Authenticate a user and return a JWT token.

        Business rules:
        - User must exist and not be soft-deleted
        - User must be active
        - Password must match the stored hash
        """
        user = self.user_repo.find_by_email(data.email)

        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedException("Account is inactive. Contact an admin.")

        # Generate token
        token = create_access_token(subject=user.id, role=user.role.value)

        return {
            "user": _user_to_dict(user),
            "token": {
                "access_token": token,
                "token_type": "bearer",
                "expires_in_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            },
        }

    def get_profile(self, user: User) -> dict:
        """Return the current user's profile."""
        return _user_to_dict(user)


def _user_to_dict(user: User) -> dict:
    """Convert a User model to a safe dict (no password)."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "status": user.status.value,
        "created_at": str(user.created_at),
    }
