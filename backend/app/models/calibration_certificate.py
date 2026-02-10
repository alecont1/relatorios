import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TenantBase


class CalibrationCertificate(TenantBase):
    """Calibration certificate model for equipment traceability."""

    __tablename__ = "calibration_certificates"
    __table_args__ = (
        UniqueConstraint("tenant_id", "certificate_number", name="uq_tenant_certificate_number"),
    )

    equipment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    certificate_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    laboratory: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    calibration_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    file_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="valid")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<CalibrationCertificate(id={self.id}, number={self.certificate_number})>"
