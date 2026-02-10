"""Drop step_users column from tenant_onboardings

The onboarding wizard was reduced from 5 to 4 steps.
The "users" step was intentionally removed from the flow.

Revision ID: 013
Revises: 012
Create Date: 2026-02-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '013'
down_revision: Union[str, None] = '012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Mark any existing pending step_users as skipped so is_completed logic works
    op.execute("UPDATE tenant_onboardings SET step_users = 'skipped' WHERE step_users = 'pending'")
    op.drop_column('tenant_onboardings', 'step_users')


def downgrade() -> None:
    op.add_column(
        'tenant_onboardings',
        sa.Column('step_users', sa.String(20), nullable=False, server_default='pending'),
    )
