"""tenant branding

Revision ID: 002
Revises: 001
Create Date: 2026-01-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add branding and contact fields to tenants table."""

    # Branding fields
    op.add_column('tenants', sa.Column('logo_primary_key', sa.String(length=500), nullable=True))
    op.add_column('tenants', sa.Column('logo_secondary_key', sa.String(length=500), nullable=True))
    op.add_column('tenants', sa.Column('brand_color_primary', sa.String(length=7), nullable=True))
    op.add_column('tenants', sa.Column('brand_color_secondary', sa.String(length=7), nullable=True))
    op.add_column('tenants', sa.Column('brand_color_accent', sa.String(length=7), nullable=True))

    # Contact fields
    op.add_column('tenants', sa.Column('contact_address', sa.String(length=500), nullable=True))
    op.add_column('tenants', sa.Column('contact_phone', sa.String(length=50), nullable=True))
    op.add_column('tenants', sa.Column('contact_email', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('contact_website', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove branding and contact fields from tenants table."""

    # Drop contact fields
    op.drop_column('tenants', 'contact_website')
    op.drop_column('tenants', 'contact_email')
    op.drop_column('tenants', 'contact_phone')
    op.drop_column('tenants', 'contact_address')

    # Drop branding fields
    op.drop_column('tenants', 'brand_color_accent')
    op.drop_column('tenants', 'brand_color_secondary')
    op.drop_column('tenants', 'brand_color_primary')
    op.drop_column('tenants', 'logo_secondary_key')
    op.drop_column('tenants', 'logo_primary_key')
