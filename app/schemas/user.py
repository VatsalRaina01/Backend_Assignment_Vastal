"""
User-related Pydantic schemas for admin user management.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    """Schema for user data in API responses — password is always excluded."""
    id: str
    email: str
    name: str
    role: str
    status: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class UpdateUserRequest(BaseModel):
    """Schema for updating user details (admin only).
    
    All fields are optional — only provided fields are updated (PATCH semantics).
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[Literal["viewer", "analyst", "admin"]] = Field(
        None, description="User role"
    )
    status: Optional[Literal["active", "inactive"]] = Field(
        None, description="Account status"
    )
    email: Optional[EmailStr] = Field(None, description="Email address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "analyst",
                "status": "active",
            }
        }
    )


class UserListParams(BaseModel):
    """Query parameters for listing users."""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    role: Optional[Literal["viewer", "analyst", "admin"]] = Field(
        None, description="Filter by role"
    )
    status: Optional[Literal["active", "inactive"]] = Field(
        None, description="Filter by status"
    )
    search: Optional[str] = Field(None, description="Search by name or email")
