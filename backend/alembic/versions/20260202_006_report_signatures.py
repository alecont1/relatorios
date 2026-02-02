"""Add report_signatures table.

Revision ID: 006
Revises: 005
Create Date: 2026-02-02

This migration adds:
- report_signatures table for storing digital signature data
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create report_signatures table
    op.create_table(
        "report_signatures",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("role_name", sa.String(100), nullable=False),
        sa.Column("signer_name", sa.String(255), nullable=True),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("report_id", sa.UUID(), nullable=False),
        sa.Column("signature_field_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["reports.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["signature_field_id"],
            ["template_signature_fields.id"],
            ondelete="SET NULL",
        ),
    )

    # Create indexes
    op.create_index("ix_report_signatures_report_id", "report_signatures", ["report_id"])
    op.create_index("ix_report_signatures_file_key", "report_signatures", ["file_key"], unique=True)
    op.create_index("ix_report_signatures_tenant_id", "report_signatures", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_report_signatures_tenant_id", table_name="report_signatures")
    op.drop_index("ix_report_signatures_file_key", table_name="report_signatures")
    op.drop_index("ix_report_signatures_report_id", table_name="report_signatures")
    op.drop_table("report_signatures")
