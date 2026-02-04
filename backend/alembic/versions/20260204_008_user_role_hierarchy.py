"""User role hierarchy and nullable tenant_id

Revision ID: 008
Revises: 007
Create Date: 2026-02-04

This migration:
1. Deletes all existing data (clean slate for new role system)
2. Makes tenant_id nullable (for superadmin users)
3. Adds CHECK constraint to enforce role/tenant_id consistency

After running this migration, create a superadmin user:
    python scripts/create_superadmin.py
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migration steps:
    1. Delete all existing data (clean slate)
    2. Make tenant_id nullable
    3. Add constraint for role/tenant consistency
    """

    # Step 1: Delete all data in correct order (respecting foreign keys)
    # Report-related tables first
    op.execute("DELETE FROM report_signatures")
    op.execute("DELETE FROM report_checklist_responses")
    op.execute("DELETE FROM report_info_values")
    op.execute("DELETE FROM report_photos")
    op.execute("DELETE FROM reports")

    # Then users
    op.execute("DELETE FROM users")

    # Optionally clean projects, templates, tenants too for fresh start
    # Uncomment if you want a completely fresh database:
    # op.execute("DELETE FROM projects")
    # op.execute("DELETE FROM template_signature_fields")
    # op.execute("DELETE FROM template_info_fields")
    # op.execute("DELETE FROM template_sections")
    # op.execute("DELETE FROM templates")
    # op.execute("DELETE FROM tenants")

    # Step 2: Make tenant_id nullable (for superadmin users)
    op.alter_column(
        'users',
        'tenant_id',
        existing_type=sa.UUID(),
        nullable=True,
    )

    # Step 3: Add CHECK constraint for role/tenant_id consistency
    op.create_check_constraint(
        'ck_user_role_tenant_consistency',
        'users',
        "(role = 'superadmin' AND tenant_id IS NULL) OR "
        "(role != 'superadmin' AND tenant_id IS NOT NULL)"
    )


def downgrade() -> None:
    """Rollback - remove constraint and make tenant_id NOT NULL"""
    op.drop_constraint('ck_user_role_tenant_consistency', 'users', type_='check')
    op.alter_column(
        'users',
        'tenant_id',
        existing_type=sa.UUID(),
        nullable=False,
    )
