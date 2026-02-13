import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantBase


class Report(TenantBase):
    """
    Report model.

    Represents a single report filled by a technician.
    Contains structured data based on a template snapshot.

    Revision system:
    - revision_number: 0 for original, incremented for each revision
    - parent_report_id: links to the original report being revised
    - is_latest_revision: only True for the most recent version
    """

    __tablename__ = "reports"

    # Report fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", index=True
    )
    location: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Geographic location as text (lat,lon)"
    )

    # Template snapshot - frozen copy at report creation for historical consistency
    template_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Lifecycle timestamps
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Revision fields
    revision_number: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    parent_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("reports.id", ondelete="SET NULL"), nullable=True, index=True
    )
    revision_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_latest_revision: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    # Foreign keys
    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Relationships
    parent_report: Mapped[Optional["Report"]] = relationship(
        "Report",
        remote_side="Report.id",
        back_populates="revisions",
        foreign_keys=[parent_report_id],
    )
    revisions: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="parent_report",
        foreign_keys=[parent_report_id],
    )
    info_values: Mapped[list["ReportInfoValue"]] = relationship(
        "ReportInfoValue",
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    checklist_responses: Mapped[list["ReportChecklistResponse"]] = relationship(
        "ReportChecklistResponse",
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    signatures: Mapped[list["ReportSignature"]] = relationship(
        "ReportSignature",
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    certificates: Mapped[list["ReportCertificate"]] = relationship(
        "ReportCertificate",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, title={self.title}, status={self.status}, rev={self.revision_number})>"
