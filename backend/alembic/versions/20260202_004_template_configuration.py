"""Template configuration schema changes

Revision ID: 004
Revises: 003
Create Date: 2026-02-02

Adds:
- template_info_fields table for project metadata configuration
- template_signature_fields table for signature requirements
- photo_config and comment_config JSONB columns to template_fields
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    # Create template_info_fields table
    op.create_table(
        "template_info_fields",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("template_id", sa.UUID(), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("field_type", sa.String(50), nullable=False),
        sa.Column("options", sa.Text(), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"], ondelete="CASCADE"),
    )

    # Create template_signature_fields table
    op.create_table(
        "template_signature_fields",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("template_id", sa.UUID(), nullable=False),
        sa.Column("role_name", sa.String(100), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"], ondelete="CASCADE"),
    )

    # Add JSONB columns to template_fields
    op.add_column("template_fields", sa.Column("photo_config", JSONB(), nullable=True))
    op.add_column("template_fields", sa.Column("comment_config", JSONB(), nullable=True))


def downgrade():
    op.drop_column("template_fields", "comment_config")
    op.drop_column("template_fields", "photo_config")
    op.drop_table("template_signature_fields")
    op.drop_table("template_info_fields")
