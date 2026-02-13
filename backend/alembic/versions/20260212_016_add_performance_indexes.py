"""Add performance indexes for reports, checklist responses, and photos

Ensures critical lookup indexes exist for:
- reports: tenant_id, status, template_id, project_id, user_id
- report_checklist_responses: report_id
- report_photos: report_id

These indexes may already exist from model definitions; this migration
uses IF NOT EXISTS to safely add any that are missing.

Revision ID: 016
Revises: 015
Create Date: 2026-02-12
"""
from typing import Sequence, Union

from alembic import op


revision: str = '016'
down_revision: Union[str, None] = '015'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Reports table indexes
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_reports_tenant_id "
        "ON reports (tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_reports_status "
        "ON reports (status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_reports_template_id "
        "ON reports (template_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_reports_project_id "
        "ON reports (project_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_reports_user_id "
        "ON reports (user_id)"
    )

    # Composite index for common list query: tenant + status + updated_at DESC
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_reports_tenant_status_updated "
        "ON reports (tenant_id, status, updated_at DESC)"
    )

    # Report checklist responses
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_report_checklist_responses_report_id "
        "ON report_checklist_responses (report_id)"
    )

    # Report photos
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_report_photos_report_id "
        "ON report_photos (report_id)"
    )


def downgrade() -> None:
    # Only drop the composite index we explicitly added;
    # single-column indexes may have been created by the ORM.
    op.execute(
        "DROP INDEX IF EXISTS ix_reports_tenant_status_updated"
    )
