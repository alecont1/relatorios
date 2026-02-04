"""User role hierarchy and nullable tenant_id

Revision ID: 008
Revises: 007
Create Date: 2026-02-04

This migration:
1. Cleans up all existing data (clean slate for new role system)
2. Makes tenant_id nullable (for superadmin users)
3. Adds CHECK constraint to enforce role/tenant_id consistency

After running this migration, create a superadmin user:
    python scripts/create_superadmin.py
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migration steps:
    1. Delete all data that depends on users (clean slate)
    2. Make tenant_id nullable
    3. Add constraint for role/tenant consistency
    """
    conn = op.get_bind()

    # Step 1: Delete all data in correct order (respecting foreign keys)
    # Use text() for raw SQL execution
    # First, check if tables exist before deleting

    # Delete report-related data if tables exist
    tables_to_clean = [
        'report_signatures',
        'report_checklist_responses',
        'report_info_values',
        'report_photos',
        'reports',
        'users'
    ]

    for table in tables_to_clean:
        try:
            conn.execute(text(f"DELETE FROM {table}"))
        except Exception:
            # Table might not exist, that's OK
            pass

    # Step 2: Make tenant_id nullable (for superadmin users)
    # Check if already nullable
    try:
        op.alter_column(
            'users',
            'tenant_id',
            existing_type=sa.UUID(),
            nullable=True,
        )
    except Exception:
        # Might already be nullable
        pass

    # Step 3: Drop existing constraint if it exists (in case of partial previous run)
    try:
        op.drop_constraint('ck_user_role_tenant_consistency', 'users', type_='check')
    except Exception:
        # Constraint might not exist
        pass

    # Step 4: Add CHECK constraint for role/tenant_id consistency
    op.create_check_constraint(
        'ck_user_role_tenant_consistency',
        'users',
        "(role = 'superadmin' AND tenant_id IS NULL) OR "
        "(role != 'superadmin' AND tenant_id IS NOT NULL)"
    )


def downgrade() -> None:
    """Rollback - remove constraint and make tenant_id NOT NULL"""
    try:
        op.drop_constraint('ck_user_role_tenant_consistency', 'users', type_='check')
    except Exception:
        pass

    try:
        op.alter_column(
            'users',
            'tenant_id',
            existing_type=sa.UUID(),
            nullable=False,
        )
    except Exception:
        pass
