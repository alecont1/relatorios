"""
User schemas for API request/response validation.

Role Hierarchy (highest to lowest privilege):
- superadmin: Global system admin, tenant_id = NULL
- tenant_admin: Admin of a specific tenant
- project_manager: Manager of specific projects
- technician: Field technician (default)
- viewer: Read-only access
"""

import re
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserRole(str, Enum):
    """
    Role hierarchy (highest to lowest privilege):
    - superadmin: Global system admin, tenant_id = NULL
    - tenant_admin: Admin of a specific tenant
    - project_manager: Manager of specific projects
    - technician: Field technician (default)
    - viewer: Read-only access
    """
    SUPERADMIN = "superadmin"
    TENANT_ADMIN = "tenant_admin"
    PROJECT_MANAGER = "project_manager"
    TECHNICIAN = "technician"
    VIEWER = "viewer"


# Role hierarchy for permission checks (higher number = more privilege)
ROLE_HIERARCHY = {
    UserRole.SUPERADMIN: 100,
    UserRole.TENANT_ADMIN: 80,
    UserRole.PROJECT_MANAGER: 60,
    UserRole.TECHNICIAN: 40,
    UserRole.VIEWER: 20,
}

# Roles that require a tenant_id (all except superadmin)
TENANT_BOUND_ROLES = {
    UserRole.TENANT_ADMIN,
    UserRole.PROJECT_MANAGER,
    UserRole.TECHNICIAN,
    UserRole.VIEWER,
}

# Roles that can manage users
USER_MANAGEMENT_ROLES = {
    UserRole.SUPERADMIN,
    UserRole.TENANT_ADMIN,
}


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
    """
    Schema for creating a new user.

    Validation rules:
    - superadmin: tenant_id must be NULL
    - All other roles: tenant_id is required
    """
    password: str
    role: UserRole = Field(default=UserRole.TECHNICIAN)
    tenant_id: UUID | None = None  # Required for non-superadmin roles

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements."""
        return validate_strong_password(v)

    @model_validator(mode="after")
    def validate_role_tenant_consistency(self) -> "UserCreate":
        """Ensure tenant_id is provided for tenant-bound roles."""
        if self.role in TENANT_BOUND_ROLES and self.tenant_id is None:
            raise ValueError(f"tenant_id é obrigatório para o cargo '{self.role.value}'")
        if self.role == UserRole.SUPERADMIN and self.tenant_id is not None:
            raise ValueError("superadmin não pode ter tenant_id")
        return self


class UserUpdate(BaseModel):
    """Schema for updating user."""
    full_name: str | None = None
    role: UserRole | None = None
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
    role: UserRole
    tenant_id: UUID | None  # Nullable for superadmin
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
