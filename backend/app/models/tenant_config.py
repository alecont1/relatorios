"""
TenantConfig model - per-tenant configuration and status.

Stores tenant-specific settings, limits overrides, and status information.
Not tenant-scoped via TenantBase (it references tenant_id as FK directly).
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TenantConfig(Base):
    """
    Tenant configuration model.

    One-to-one relationship with Tenant. Stores operational status,
    plan assignment, resource limits, and feature overrides.
    """

    __tablename__ = "tenant_configs"

    # Foreign keys
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tenant_plans.id", ondelete="SET NULL"), nullable=True
    )

    # Status fields
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="trial")
    contract_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Limits and features (overrides from plan)
    limits_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    features_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    # Suspension tracking
    suspended_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    suspended_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Trial tracking
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="config",
        lazy="selectin"
    )
    plan: Mapped[Optional["TenantPlan"]] = relationship(
        "TenantPlan",
        back_populates="configs",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<TenantConfig(id={self.id}, tenant_id={self.tenant_id}, status={self.status})>"
