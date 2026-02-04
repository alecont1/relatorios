import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base model for all database tables.

    Provides common columns for all models:
    - id: Primary key (UUID)
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update

    NOTE: tenant_id is NOT included here. Models that need multi-tenant
    support should inherit from TenantBase instead.
    """

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class TenantBase(Base):
    """
    Base model for tables that need multi-tenant support.

    Adds tenant_id column for tenant isolation.
    Most top-level models (User, Template, Report, etc.) should inherit from this.
    """

    __abstract__ = True

    # Multi-tenant support
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        index=True,
        nullable=False
    )
