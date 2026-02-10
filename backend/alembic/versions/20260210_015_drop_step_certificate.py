"""Drop step_certificate column from tenant_onboardings

The onboarding wizard was reduced from 4 to 3 steps.
The "certificate" step was removed from the flow and moved
to the main Certificates page, accessible after onboarding.

Revision ID: 015
Revises: 014
Create Date: 2026-02-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '015'
down_revision: Union[str, None] = '014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Mark any existing pending step_certificate as skipped so is_completed logic works
    op.execute("UPDATE tenant_onboardings SET step_certificate = 'skipped' WHERE step_certificate = 'pending'")
    op.drop_column('tenant_onboardings', 'step_certificate')


def downgrade() -> None:
    op.add_column(
        'tenant_onboardings',
        sa.Column('step_certificate', sa.String(20), nullable=False, server_default='pending'),
    )
