import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.simple_base import SimpleBase


class TemplateField(SimpleBase):
    """
    Template field model.

    Fields represent individual checklist items within a section.
    Fields have types (dropdown, text) and optional configurations (options for dropdowns).

    Tenant isolation: Inherited through parent Section -> Template (no direct tenant_id).
    """

    __tablename__ = "template_fields"

    # Foreign key to parent section
    section_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("template_sections.id", ondelete="CASCADE"),
        nullable=False
    )

    # Field configuration
    label: Mapped[str] = mapped_column(String(500), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)
    options: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array for dropdown options
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Photo and comment configuration (JSONB for flexible structure)
    photo_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Schema: {"required": bool, "min_count": int, "max_count": int, "require_gps": bool, "watermark": bool}

    comment_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Schema: {"enabled": bool, "required": bool}

    # Relationships
    section: Mapped["TemplateSection"] = relationship(
        "TemplateSection",
        back_populates="fields"
    )

    def __repr__(self) -> str:
        return f"<TemplateField(id={self.id}, label={self.label}, type={self.field_type})>"
