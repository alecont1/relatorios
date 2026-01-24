import uuid

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReportPhoto(Base):
    """
    ReportPhoto model.

    Represents a photo attached to a report.
    Photos are stored in Cloudflare R2, this tracks metadata.
    """

    __tablename__ = "report_photos"

    # Photo metadata
    file_key: Mapped[str] = mapped_column(
        String(500), nullable=False, unique=True, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    location: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Geographic location as text (lat,lon) - Phase 1"
    )
    watermark_applied: Mapped[bool] = mapped_column(default=False, nullable=False)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign keys
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<ReportPhoto(id={self.id}, file_key={self.file_key})>"
