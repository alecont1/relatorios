import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.simple_base import SimpleBase


class TemplateSection(SimpleBase):
    """
    Template section model.

    Sections group related fields within a template.
    Sections are ordered and cascade-deleted when their parent template is deleted.

    Tenant isolation: Inherited through parent Template (no direct tenant_id).
    """

    __tablename__ = "template_sections"

    # Foreign key to parent template
    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False
    )

    # Section fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    template: Mapped["Template"] = relationship(
        "Template",
        back_populates="sections"
    )

    fields: Mapped[list["TemplateField"]] = relationship(
        "TemplateField",
        back_populates="section",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<TemplateSection(id={self.id}, name={self.name}, order={self.order})>"
