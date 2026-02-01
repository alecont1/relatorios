"""template tables

Revision ID: 003
Revises: 002
Create Date: 2026-01-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create template, template_sections, and template_fields tables."""

    # Drop old templates table if exists (from initial schema)
    op.drop_table('templates')

    # Create new templates table with full schema
    op.create_table(
        'templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('reference_standards', sa.Text(), nullable=True),
        sa.Column('planning_requirements', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_templates_tenant_id'),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_template_tenant_code')
    )

    # Create template_sections table
    op.create_table(
        'template_sections',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('template_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], name='fk_template_sections_template_id', ondelete='CASCADE')
    )

    # Create template_fields table
    op.create_table(
        'template_fields',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('section_id', UUID(as_uuid=True), nullable=False),
        sa.Column('label', sa.String(length=500), nullable=False),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.Column('options', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['section_id'], ['template_sections.id'], name='fk_template_fields_section_id', ondelete='CASCADE')
    )


def downgrade() -> None:
    """Drop template tables and recreate old templates stub."""

    # Drop tables in reverse order (children first)
    op.drop_table('template_fields')
    op.drop_table('template_sections')
    op.drop_table('templates')

    # Recreate old templates stub (from initial schema)
    op.create_table(
        'templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('schema_json', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_templates_tenant_id')
    )
