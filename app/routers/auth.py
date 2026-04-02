"""
Auth router — registration, login, and profile endpoints.

Public endpoints (register/login) are rate-limited to prevent brute-force.
Profile endpoint requires authentication.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", status_code=201, summary="Register a new user")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account.

    - New users are assigned the **viewer** role by default.
    - Returns a JWT token immediately (auto-login after registration).
    - Email must be unique.
    """
    service = AuthService(db)
    result = service.register(data)
    return success_response(data=result, message="User registered successfully")


@router.post("/login", summary="Login and get JWT token")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password.

    Returns a JWT token that must be included in the `Authorization: Bearer <token>`
    header for all protected endpoints.
    """
    service = AuthService(db)
    result = service.login(data)
    return success_response(data=result, message="Login successful")


@router.get("/me", summary="Get current user profile")
def get_me(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's profile.

    Requires a valid JWT token in the Authorization header.
    """
    service = AuthService.__new__(AuthService)  # No DB needed for profile
    result = service.get_profile(current_user)
    return success_response(data=result, message="Profile retrieved")
