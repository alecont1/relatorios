"""Add report revision fields

Adds revision tracking columns to the reports table:
- revision_number: integer, default 0
- parent_report_id: FK to reports.id (self-referential)
- revision_notes: text for describing what changed
- is_latest_revision: boolean flag for filtering

Revision ID: 017
Revises: 016
Create Date: 2026-02-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '017'
down_revision: Union[str, None] = '016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add revision_number with default 0
    op.add_column(
        'reports',
        sa.Column('revision_number', sa.Integer(), nullable=False, server_default='0'),
    )

    # Add parent_report_id (self-referential FK)
    op.add_column(
        'reports',
        sa.Column('parent_report_id', sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        'fk_reports_parent_report',
        'reports', 'reports',
        ['parent_report_id'], ['id'],
        ondelete='SET NULL',
    )
    op.create_index('ix_reports_parent_report_id', 'reports', ['parent_report_id'])

    # Add revision_notes
    op.add_column(
        'reports',
        sa.Column('revision_notes', sa.Text(), nullable=True),
    )

    # Add is_latest_revision with default True
    op.add_column(
        'reports',
        sa.Column('is_latest_revision', sa.Boolean(), nullable=False, server_default='true'),
    )


def downgrade() -> None:
    op.drop_column('reports', 'is_latest_revision')
    op.drop_column('reports', 'revision_notes')
    op.drop_index('ix_reports_parent_report_id', 'reports')
    op.drop_constraint('fk_reports_parent_report', 'reports', type_='foreignkey')
    op.drop_column('reports', 'parent_report_id')
    op.drop_column('reports', 'revision_number')
