"""tenant watermark

Revision ID: 007
Revises: 006
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add watermark_text field to tenants table."""
    op.add_column('tenants', sa.Column('watermark_text', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove watermark_text field from tenants table."""
    op.drop_column('tenants', 'watermark_text')
