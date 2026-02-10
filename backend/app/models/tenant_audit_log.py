"""
TenantAuditLog model - immutable audit trail for tenant management actions.

Records all SuperAdmin actions on tenants for compliance and debugging.
Not tenant-scoped via TenantBase (references tenant_id as FK directly).
"""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TenantAuditLog(Base):
    """
    Tenant audit log model.

    Immutable record of administrative actions performed on tenants.
    Used for compliance tracking and operational debugging.
    """

    __tablename__ = "tenant_audit_logs"

    # Foreign keys
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Action details
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    old_values: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    def __repr__(self) -> str:
        return f"<TenantAuditLog(id={self.id}, tenant_id={self.tenant_id}, action={self.action})>"
