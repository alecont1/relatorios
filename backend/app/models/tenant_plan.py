"""
TenantPlan model - global plan definitions for tenants.

Plans define limits and features available to tenants.
Not tenant-scoped (extends Base, not TenantBase).
"""

import uuid
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TenantPlan(Base):
    """
    Tenant plan model.

    Represents a subscription/service plan that can be assigned to tenants.
    Plans define resource limits and feature flags.
    """

    __tablename__ = "tenant_plans"

    # Plan fields
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    limits_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    features_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    price_display: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    configs: Mapped[list["TenantConfig"]] = relationship(
        "TenantConfig",
        back_populates="plan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<TenantPlan(id={self.id}, name={self.name}, is_active={self.is_active})>"
