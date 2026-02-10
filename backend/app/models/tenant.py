import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tenant(Base):
    """
    Tenant model - NO tenant_id column (it IS a tenant).

    Represents a customer organization in the multi-tenant system.
    All other entities belong to a tenant.
    """

    __tablename__ = "tenants"

    # Tenant-specific fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Branding fields (for TNNT-03 and TNNT-04)
    logo_primary_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo_secondary_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    brand_color_primary: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    brand_color_secondary: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    brand_color_accent: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)

    # Contact fields (for TNNT-05)
    contact_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Watermark field (for report branding)
    watermark_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Watermark configuration (JSONB)
    watermark_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # PDF Layout preference
    default_pdf_layout_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("pdf_layouts.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    config: Mapped[Optional["TenantConfig"]] = relationship(
        "TenantConfig",
        back_populates="tenant",
        uselist=False,
        lazy="selectin"
    )
    onboarding: Mapped[Optional["TenantOnboarding"]] = relationship(
        "TenantOnboarding",
        back_populates="tenant",
        uselist=False,
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, slug={self.slug}, name={self.name})>"
