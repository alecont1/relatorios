"""
TenantOnboarding model - tracks guided onboarding progress per tenant.

Stores step completion status for the 4-step onboarding wizard.
Not tenant-scoped via TenantBase (it references tenant_id as FK directly).
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TenantOnboarding(Base):
    """
    Tenant onboarding progress model.

    One-to-one relationship with Tenant. Tracks completion of the
    4-step guided onboarding wizard for new tenants.

    Step status values: "pending" | "completed" | "skipped"
    """

    __tablename__ = "tenant_onboardings"

    # Foreign key
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )

    # Overall completion
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Step statuses
    step_branding: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    step_template: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    step_certificate: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    step_first_report: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    # Current step index (0-3) for recovery
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Metadata (stores demo_template_id, first_report_id, etc.)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    # Relationships
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="onboarding",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<TenantOnboarding(id={self.id}, tenant_id={self.tenant_id}, is_completed={self.is_completed})>"
