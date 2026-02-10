"""Tenant onboarding progress tracking

Revision ID: 012
Revises: 011
Create Date: 2026-02-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = '012'
down_revision: Union[str, None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tenant_onboardings',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('step_branding', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('step_template', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('step_certificate', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('step_users', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('step_first_report', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('current_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('metadata_json', JSONB, server_default='{}', nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tenant_onboardings_tenant_id', 'tenant_onboardings', ['tenant_id'], unique=True)


def downgrade() -> None:
    op.drop_table('tenant_onboardings')
