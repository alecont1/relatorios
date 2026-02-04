"""
User model with role-based multi-tenant support.

Role Hierarchy:
- superadmin: Global admin (tenant_id = NULL)
- tenant_admin: Admin of a specific tenant
- project_manager: Manager of specific projects
- technician: Field technician (default)
- viewer: Read-only access
"""

import uuid
from typing import Optional

from sqlalchemy import String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    """
    User model.

    Represents a user within the system.
    - superadmin users have tenant_id = NULL
    - All other roles require a tenant_id

    The database constraint ensures data integrity:
    - role = 'superadmin' AND tenant_id IS NULL
    - role != 'superadmin' AND tenant_id IS NOT NULL
    """

    __tablename__ = "users"

    # Multi-tenant support - NULLABLE for superadmin
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        index=True,
        nullable=True,
    )

    # User fields
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="technician")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Database-level constraint to enforce role/tenant_id relationship
    __table_args__ = (
        CheckConstraint(
            "(role = 'superadmin' AND tenant_id IS NULL) OR "
            "(role != 'superadmin' AND tenant_id IS NOT NULL)",
            name="ck_user_role_tenant_consistency"
        ),
    )

    @property
    def is_superadmin(self) -> bool:
        """Check if user is a superadmin."""
        return self.role == "superadmin"

    @property
    def is_tenant_admin(self) -> bool:
        """Check if user is a tenant admin."""
        return self.role == "tenant_admin"

    @property
    def is_project_manager(self) -> bool:
        """Check if user is a project manager."""
        return self.role == "project_manager"

    @property
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role in ("superadmin", "tenant_admin")

    @property
    def can_manage_templates(self) -> bool:
        """Check if user can manage templates."""
        return self.role in ("superadmin", "tenant_admin")

    @property
    def can_manage_projects(self) -> bool:
        """Check if user can manage projects."""
        return self.role in ("superadmin", "tenant_admin", "project_manager")

    def can_manage_role(self, target_role: str) -> bool:
        """
        Check if this user can manage users with the target role.

        Rules:
        - superadmin can manage all roles
        - tenant_admin can manage: project_manager, technician, viewer
        - project_manager cannot manage users
        - technician cannot manage users
        - viewer cannot manage users
        """
        role_hierarchy = {
            "superadmin": 100,
            "tenant_admin": 80,
            "project_manager": 60,
            "technician": 40,
            "viewer": 20,
        }
        my_level = role_hierarchy.get(self.role, 0)
        target_level = role_hierarchy.get(target_role, 0)
        return my_level > target_level

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role}, tenant_id={self.tenant_id})>"
