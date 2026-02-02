import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.simple_base import SimpleBase


class ReportChecklistResponse(SimpleBase):
    """
    Stores a single checklist field response for a report.

    Captures the user's answer to each checklist question, along with
    optional comments and photo references.

    Uses SimpleBase (no tenant_id) - tenant isolation via parent Report.
    """

    __tablename__ = "report_checklist_responses"

    # Foreign keys
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("template_sections.id", ondelete="SET NULL"), nullable=True
    )
    field_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("template_fields.id", ondelete="SET NULL"), nullable=True
    )

    # Denormalized for snapshot (template structure may change)
    section_name: Mapped[str] = mapped_column(String(255), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    field_label: Mapped[str] = mapped_column(String(500), nullable=False)
    field_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)
    field_options: Mapped[str | None] = mapped_column(Text, nullable=True)

    # The actual response filled by user
    response_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Photo references (array of {photo_id, url, caption})
    # Will be populated in Phase 7
    photos: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    # Relationships
    report: Mapped["Report"] = relationship(back_populates="checklist_responses")

    def __repr__(self) -> str:
        return f"<ReportChecklistResponse(field_label={self.field_label}, response={self.response_value})>"
