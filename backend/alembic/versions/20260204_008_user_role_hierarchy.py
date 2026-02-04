"""User role hierarchy and nullable tenant_id

Revision ID: 008
Revises: 007
Create Date: 2026-02-04

This migration:
1. Makes tenant_id nullable (for superadmin users)
2. Maps old roles to new role hierarchy:
   - admin -> tenant_admin
   - manager -> project_manager
   - user -> technician
3. Adds CHECK constraint to enforce role/tenant_id consistency:
   - superadmin: tenant_id MUST be NULL
   - All other roles: tenant_id MUST NOT be NULL
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migration steps:
    1. Make tenant_id nullable
    2. Update existing roles to new hierarchy
    3. Add constraint for role/tenant consistency
    """

    # Step 1: Make tenant_id nullable
    # This allows superadmin users to have NULL tenant_id
    op.alter_column(
        'users',
        'tenant_id',
        existing_type=sa.UUID(),
        nullable=True,
    )

    # Step 2: Update existing roles to new hierarchy
    # Map old roles to new roles:
    # - admin -> tenant_admin (admin of a tenant)
    # - manager -> project_manager (manager of projects)
    # - user -> technician (field technician)
    # - global_admin -> superadmin (if exists)
    # - technician stays technician
    # - viewer stays viewer (if exists)
    op.execute("""
        UPDATE users SET role =
            CASE role
                WHEN 'admin' THEN 'tenant_admin'
                WHEN 'manager' THEN 'project_manager'
                WHEN 'user' THEN 'technician'
                WHEN 'global_admin' THEN 'superadmin'
                ELSE role
            END
        WHERE role IN ('admin', 'manager', 'user', 'global_admin')
    """)

    # Step 3: Add CHECK constraint for role/tenant_id consistency
    # This ensures data integrity at the database level:
    # - superadmin users MUST have tenant_id = NULL
    # - All other users MUST have tenant_id != NULL
    op.create_check_constraint(
        'ck_user_role_tenant_consistency',
        'users',
        "(role = 'superadmin' AND tenant_id IS NULL) OR "
        "(role != 'superadmin' AND tenant_id IS NOT NULL)"
    )


def downgrade() -> None:
    """
    Rollback steps:
    1. Remove constraint
    2. Revert roles (best effort)
    3. Make tenant_id NOT NULL (will fail if superadmin exists)

    WARNING: Downgrade may fail if superadmin users exist with NULL tenant_id.
    You must manually assign tenant_id or delete superadmin users first.
    """

    # Step 1: Remove constraint
    op.drop_constraint('ck_user_role_tenant_consistency', 'users', type_='check')

    # Step 2: Revert roles
    # Note: This is best effort - some information is lost
    # - tenant_admin -> admin
    # - project_manager -> manager
    # - technician -> user
    # - viewer -> user (no direct mapping)
    # - superadmin -> admin (will fail constraint later if tenant_id is NULL)
    op.execute("""
        UPDATE users SET role =
            CASE role
                WHEN 'tenant_admin' THEN 'admin'
                WHEN 'project_manager' THEN 'manager'
                WHEN 'technician' THEN 'user'
                WHEN 'viewer' THEN 'user'
                WHEN 'superadmin' THEN 'admin'
                ELSE role
            END
    """)

    # Step 3: Make tenant_id NOT NULL
    # WARNING: This will fail if any users have NULL tenant_id
    # You must manually fix superadmin users before running downgrade
    op.alter_column(
        'users',
        'tenant_id',
        existing_type=sa.UUID(),
        nullable=False,
    )
