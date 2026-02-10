"""Tenant plans, configs, and audit logs for SuperAdmin management

Revision ID: 011
Revises: 010
Create Date: 2026-02-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- tenant_plans ---
    op.create_table(
        'tenant_plans',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('limits_json', JSONB, server_default='{}', nullable=False),
        sa.Column('features_json', JSONB, server_default='{}', nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('price_display', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # --- tenant_configs ---
    op.create_table(
        'tenant_configs',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('plan_id', sa.UUID(), sa.ForeignKey('tenant_plans.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='trial'),
        sa.Column('contract_type', sa.String(50), nullable=True),
        sa.Column('limits_json', JSONB, server_default='{}', nullable=False),
        sa.Column('features_json', JSONB, server_default='{}', nullable=False),
        sa.Column('suspended_at', sa.DateTime(), nullable=True),
        sa.Column('suspended_reason', sa.Text(), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tenant_configs_tenant_id', 'tenant_configs', ['tenant_id'], unique=True)
    op.create_index('ix_tenant_configs_plan_id', 'tenant_configs', ['plan_id'])

    # --- tenant_audit_logs ---
    op.create_table(
        'tenant_audit_logs',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('tenant_id', sa.UUID(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('admin_user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('old_values', JSONB, nullable=True),
        sa.Column('new_values', JSONB, nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tenant_audit_logs_tenant_id', 'tenant_audit_logs', ['tenant_id'])
    op.create_index('ix_tenant_audit_logs_action', 'tenant_audit_logs', ['action'])


def downgrade() -> None:
    op.drop_table('tenant_audit_logs')
    op.drop_table('tenant_configs')
    op.drop_table('tenant_plans')
