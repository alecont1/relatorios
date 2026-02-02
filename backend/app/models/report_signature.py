import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ReportSignature(Base):
    """
    ReportSignature model.

    Represents a digital signature captured for a report.
    Signatures are linked to template signature fields (roles like Technician, Supervisor, Client).
    The actual signature image is stored in R2.
    """

    __tablename__ = "report_signatures"

    # Signature metadata
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    signer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # R2 storage
    file_key: Mapped[str] = mapped_column(
        String(500), nullable=False, unique=True, index=True
    )

    # Timestamp when signature was captured
    signed_at: Mapped[datetime] = mapped_column(nullable=False)

    # Foreign keys
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    signature_field_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("template_signature_fields.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relationships
    report: Mapped["Report"] = relationship(back_populates="signatures")

    def __repr__(self) -> str:
        return f"<ReportSignature(id={self.id}, role={self.role_name})>"
