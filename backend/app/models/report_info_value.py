import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.simple_base import SimpleBase


class ReportInfoValue(SimpleBase):
    """
    Stores a single info field value for a report.

    Info values capture project metadata (e.g., project name, date, location)
    that the user fills at the start of a report.

    Uses SimpleBase (no tenant_id) - tenant isolation via parent Report.
    """

    __tablename__ = "report_info_values"

    # Foreign keys
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    info_field_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("template_info_fields.id", ondelete="SET NULL"), nullable=True
    )

    # Denormalized for snapshot (field may be deleted later)
    field_label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # The actual value filled by user
    value: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    report: Mapped["Report"] = relationship(back_populates="info_values")

    def __repr__(self) -> str:
        return f"<ReportInfoValue(field_label={self.field_label}, value={self.value})>"
