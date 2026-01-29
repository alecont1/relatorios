"""
User schemas for API request/response validation.
"""

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_strong_password(password: str) -> str:
    """
    Validate password meets strength requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one number
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        The password if valid

    Raises:
        ValueError: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise ValueError("Senha deve ter no minimo 8 caracteres")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Senha deve conter pelo menos uma letra maiuscula")
    if not re.search(r"[0-9]", password):
        raise ValueError("Senha deve conter pelo menos um numero")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Senha deve conter pelo menos um caractere especial")
    return password


class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user (admin only)."""
    password: str
    role: str = Field(default="user", pattern="^(user|manager|admin)$")
    tenant_id: UUID | None = None  # Only superadmin can specify

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements."""
        return validate_strong_password(v)


class UserUpdate(BaseModel):
    """Schema for updating user (admin only)."""
    full_name: str | None = None
    role: str | None = Field(default=None, pattern="^(user|manager|admin)$")
    is_active: bool | None = None
    password: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str | None) -> str | None:
        """Validate password meets strength requirements if provided."""
        if v is not None:
            return validate_strong_password(v)
        return v


class UserResponse(UserBase):
    """User data returned in API responses."""
    id: UUID
    role: str
    tenant_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Paginated list of users."""
    users: list[UserResponse]
    total: int


class UserWithToken(BaseModel):
    """Login response with user data and access token."""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
