import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.simple_base import SimpleBase


class TemplateSignatureField(SimpleBase):
    """
    Template signature field model.

    Signature fields define who needs to sign the report (e.g., Technician, Supervisor, Client).
    Each signature field can be required or optional.

    These are template-level configuration, defining the signature requirements
    for reports generated from this template.

    Tenant isolation: Inherited through parent Template (no direct tenant_id).
    """

    __tablename__ = "template_signature_fields"

    # Foreign key to parent template
    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False
    )

    # Signature configuration
    role_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # e.g., "Technician", "Supervisor", "Client"
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    template: Mapped["Template"] = relationship(
        "Template",
        back_populates="signature_fields"
    )

    def __repr__(self) -> str:
        return f"<TemplateSignatureField(id={self.id}, role={self.role_name})>"
