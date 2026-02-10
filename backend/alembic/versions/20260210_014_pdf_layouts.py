"""Add pdf_layouts table and layout references

Creates the pdf_layouts table for customizable PDF report layouts.
Adds default_pdf_layout_id to tenants and pdf_layout_id to templates.

Revision ID: 014
Revises: 013
Create Date: 2026-02-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = '014'
down_revision: Union[str, None] = '013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create pdf_layouts table
    op.create_table(
        'pdf_layouts',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config_json', JSONB(), server_default='{}', nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('tenant_id', 'slug', name='uq_pdf_layout_tenant_slug'),
    )
    op.create_index('ix_pdf_layouts_tenant_id', 'pdf_layouts', ['tenant_id'])

    # 2. Add default_pdf_layout_id to tenants
    op.add_column(
        'tenants',
        sa.Column('default_pdf_layout_id', sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        'fk_tenants_default_pdf_layout',
        'tenants', 'pdf_layouts',
        ['default_pdf_layout_id'], ['id'],
        ondelete='SET NULL',
    )

    # 3. Add pdf_layout_id to templates
    op.add_column(
        'templates',
        sa.Column('pdf_layout_id', sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        'fk_templates_pdf_layout',
        'templates', 'pdf_layouts',
        ['pdf_layout_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    # 3. Drop pdf_layout_id from templates
    op.drop_constraint('fk_templates_pdf_layout', 'templates', type_='foreignkey')
    op.drop_column('templates', 'pdf_layout_id')

    # 2. Drop default_pdf_layout_id from tenants
    op.drop_constraint('fk_tenants_default_pdf_layout', 'tenants', type_='foreignkey')
    op.drop_column('tenants', 'default_pdf_layout_id')

    # 1. Drop pdf_layouts table
    op.drop_index('ix_pdf_layouts_tenant_id', 'pdf_layouts')
    op.drop_table('pdf_layouts')
