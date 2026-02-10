import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PdfLayout(Base):
    """
    PDF Layout model for customizable report layouts.

    System layouts (is_system=True) have tenant_id=NULL and are available to all tenants.
    Custom layouts belong to a specific tenant and require the custom_pdf feature.
    """

    __tablename__ = "pdf_layouts"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    is_system: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_pdf_layout_tenant_slug"),
    )

    def __repr__(self) -> str:
        return f"<PdfLayout(id={self.id}, slug={self.slug}, name={self.name})>"
