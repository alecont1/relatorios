"""
User schemas for API request/response validation.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user (admin only)."""
    password: str = Field(
        min_length=8,
        description="Minimum 8 characters, must include uppercase, number, and special character"
    )
    role: str = Field(default="user", pattern="^(user|manager|admin)$")
    # tenant_id is set from current_user for admin, or specified by superadmin


class UserResponse(UserBase):
    """User data returned in API responses."""
    id: UUID
    role: str
    tenant_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserWithToken(BaseModel):
    """Login response with user data and access token."""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
