"""
FastAPI dependencies — the core of our request pipeline.

These are injected into route handlers via FastAPI's Depends() system.
Flow: get_db → get_current_user → RoleChecker
"""

from typing import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User, UserStatus
from app.utils.exceptions import ForbiddenException, UnauthorizedException
from app.utils.security import decode_access_token


# HTTP Bearer scheme — Swagger shows a simple "Bearer token" input
bearer_scheme = HTTPBearer(
    auto_error=False,  # We handle missing token ourselves (return 401, not 403)
    description="Paste your JWT token here (obtained from /api/v1/auth/login)"
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session, ensuring cleanup on completion.

    Used as a dependency in every route that needs DB access.
    The session is committed by the route handler; this just ensures
    the connection is closed even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT token.

    This dependency:
    1. Decodes the JWT from the Authorization header
    2. Looks up the user in the database
    3. Verifies the user is active and not soft-deleted
    4. Returns the User object for downstream use

    Raises:
        UnauthorizedException: If the token is invalid, user not found, or user inactive.
    """
    if credentials is None:
        raise UnauthorizedException("Authentication required")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Invalid token: missing subject")
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise UnauthorizedException("User not found")
    if user.deleted_at is not None:
        raise UnauthorizedException("Account has been deactivated")
    if user.status != UserStatus.ACTIVE:
        raise UnauthorizedException("Account is inactive")

    return user


class RoleChecker:
    """Reusable dependency for role-based access control.

    Usage in routers:
        allow_admin = RoleChecker(["admin"])
        allow_analyst_admin = RoleChecker(["analyst", "admin"])

        @router.get("/endpoint", dependencies=[Depends(allow_admin)])
        def protected_route(): ...

    Or inject the user directly:
        @router.get("/endpoint")
        def protected_route(user: User = Depends(allow_admin)): ...
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role.value not in self.allowed_roles:
            raise ForbiddenException(
                f"Role '{user.role.value}' does not have access. "
                f"Required: {', '.join(self.allowed_roles)}"
            )
        return user


# ── Pre-built role checkers (used across routers) ────────────────────────────

allow_any_authenticated = RoleChecker(["viewer", "analyst", "admin"])
allow_analyst_admin = RoleChecker(["analyst", "admin"])
allow_admin_only = RoleChecker(["admin"])
