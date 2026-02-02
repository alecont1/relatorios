"""report structured data

Revision ID: 005
Revises: 004
Create Date: 2026-02-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add structured data to reports and create child tables."""

    # 1. Add new columns to reports table
    op.add_column('reports', sa.Column('template_snapshot', JSONB(), nullable=True))
    op.add_column('reports', sa.Column('started_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('reports', sa.Column('completed_at', sa.TIMESTAMP(), nullable=True))

    # 2. Set default value for existing rows (empty snapshot)
    op.execute("UPDATE reports SET template_snapshot = '{}'::jsonb WHERE template_snapshot IS NULL")

    # 3. Make template_snapshot NOT NULL after setting defaults
    op.alter_column('reports', 'template_snapshot', nullable=False)

    # 4. Drop data_json column (no longer needed)
    op.drop_column('reports', 'data_json')

    # 5. Create report_info_values table
    op.create_table(
        'report_info_values',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('report_id', UUID(as_uuid=True), nullable=False),
        sa.Column('info_field_id', UUID(as_uuid=True), nullable=True),
        sa.Column('field_label', sa.String(length=255), nullable=False),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], name='fk_report_info_values_report_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['info_field_id'], ['template_info_fields.id'], name='fk_report_info_values_info_field_id', ondelete='SET NULL'),
    )
    op.create_index('ix_report_info_values_report_id', 'report_info_values', ['report_id'])

    # 6. Create report_checklist_responses table
    op.create_table(
        'report_checklist_responses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('report_id', UUID(as_uuid=True), nullable=False),
        sa.Column('section_id', UUID(as_uuid=True), nullable=True),
        sa.Column('field_id', UUID(as_uuid=True), nullable=True),
        sa.Column('section_name', sa.String(length=255), nullable=False),
        sa.Column('section_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('field_label', sa.String(length=500), nullable=False),
        sa.Column('field_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.Column('field_options', sa.Text(), nullable=True),
        sa.Column('response_value', sa.Text(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('photos', JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], name='fk_report_checklist_responses_report_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['section_id'], ['template_sections.id'], name='fk_report_checklist_responses_section_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['field_id'], ['template_fields.id'], name='fk_report_checklist_responses_field_id', ondelete='SET NULL'),
    )
    op.create_index('ix_report_checklist_responses_report_id', 'report_checklist_responses', ['report_id'])


def downgrade() -> None:
    """Revert report structured data changes."""

    # Drop child tables
    op.drop_index('ix_report_checklist_responses_report_id', table_name='report_checklist_responses')
    op.drop_table('report_checklist_responses')

    op.drop_index('ix_report_info_values_report_id', table_name='report_info_values')
    op.drop_table('report_info_values')

    # Add back data_json column
    op.add_column('reports', sa.Column('data_json', sa.Text(), nullable=True))
    op.execute("UPDATE reports SET data_json = '{}'")
    op.alter_column('reports', 'data_json', nullable=False)

    # Drop new columns from reports
    op.drop_column('reports', 'completed_at')
    op.drop_column('reports', 'started_at')
    op.drop_column('reports', 'template_snapshot')
