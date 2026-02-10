import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.simple_base import SimpleBase


class ReportCertificate(SimpleBase):
    """Association between reports and calibration certificates."""

    __tablename__ = "report_certificates"
    __table_args__ = (
        UniqueConstraint("report_id", "certificate_id", name="uq_report_certificate"),
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    certificate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("calibration_certificates.id", ondelete="CASCADE"), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<ReportCertificate(report_id={self.report_id}, certificate_id={self.certificate_id})>"
