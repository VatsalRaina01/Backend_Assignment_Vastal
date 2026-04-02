"""
Auth-related Pydantic schemas for request/response validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="Password (min 8 characters)"
    )
    name: str = Field(
        ..., min_length=1, max_length=100, description="User's full name"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "password": "securepass123",
                "name": "John Doe",
            }
        }
    )


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@example.com",
                "password": "admin123456",
            }
        }
    )


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserProfileResponse(BaseModel):
    """Schema for the authenticated user's profile — never includes password."""
    id: str
    email: str
    name: str
    role: str
    status: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)
