import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.simple_base import SimpleBase


class TemplateInfoField(SimpleBase):
    """
    Template info field model.

    Info fields represent project metadata that needs to be filled when creating a report
    (e.g., Project Name, Date, Location, Client).

    These are template-level fields, not section-level fields. They appear at the top
    of reports before the checklist sections.

    Tenant isolation: Inherited through parent Template (no direct tenant_id).
    """

    __tablename__ = "template_info_fields"

    # Foreign key to parent template
    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False
    )

    # Field configuration
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # Values: "text", "date", "select"
    options: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON array for select options
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    template: Mapped["Template"] = relationship(
        "Template",
        back_populates="info_fields"
    )

    def __repr__(self) -> str:
        return f"<TemplateInfoField(id={self.id}, label={self.label}, type={self.field_type})>"
