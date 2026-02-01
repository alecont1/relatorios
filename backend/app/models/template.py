import uuid

from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Template(Base):
    """
    Template model for report generation.

    Templates define the structure of reports with metadata, header information,
    and a hierarchical structure of sections containing fields.

    Tenant isolation: Each template belongs to a specific tenant via tenant_id.
    """

    __tablename__ = "templates"

    # Core metadata fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Header fields (for report generation)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reference_standards: Mapped[str | None] = mapped_column(Text, nullable=True)
    planning_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    sections: Mapped[list["TemplateSection"]] = relationship(
        "TemplateSection",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateSection.order"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_template_tenant_code"),
    )

    def __repr__(self) -> str:
        return f"<Template(id={self.id}, name={self.name}, code={self.code})>"
