import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Report(Base):
    """
    Report model.

    Represents a single report filled by a technician.
    Contains structured data based on a template.
    """

    __tablename__ = "reports"

    # Report fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", index=True
    )
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Geographic location as text (lat,lon) - Phase 1"
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

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, title={self.title}, status={self.status})>"
