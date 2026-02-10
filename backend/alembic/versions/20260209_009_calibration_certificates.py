"""Calibration certificates and report-certificate association

Revision ID: 009
Revises: 008
Create Date: 2026-02-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'calibration_certificates',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('equipment_name', sa.String(255), nullable=False),
        sa.Column('certificate_number', sa.String(100), nullable=False),
        sa.Column('manufacturer', sa.String(255), nullable=True),
        sa.Column('model', sa.String(255), nullable=True),
        sa.Column('serial_number', sa.String(255), nullable=True),
        sa.Column('laboratory', sa.String(255), nullable=True),
        sa.Column('calibration_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('file_key', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='valid'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'certificate_number', name='uq_tenant_certificate_number'),
    )
    op.create_index('ix_calibration_certificates_tenant_id', 'calibration_certificates', ['tenant_id'])
    op.create_index('ix_calibration_certificates_certificate_number', 'calibration_certificates', ['certificate_number'])

    op.create_table(
        'report_certificates',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('report_id', sa.UUID(), sa.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('certificate_id', sa.UUID(), sa.ForeignKey('calibration_certificates.id', ondelete='CASCADE'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_id', 'certificate_id', name='uq_report_certificate'),
    )
    op.create_index('ix_report_certificates_report_id', 'report_certificates', ['report_id'])
    op.create_index('ix_report_certificates_certificate_id', 'report_certificates', ['certificate_id'])


def downgrade() -> None:
    op.drop_table('report_certificates')
    op.drop_table('calibration_certificates')
