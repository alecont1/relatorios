import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    Base model for all database tables.

    Provides common columns for all models:
    - id: Primary key (UUID)
    - tenant_id: Multi-tenant support (indexed) - except for Tenant model
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update

    All models should inherit from this class.
    """

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Multi-tenant support - conditionally added
    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID]:
        """Add tenant_id to all tables except tenants."""
        if cls.__name__ == "Tenant":
            # Tenant table doesn't have tenant_id
            return None  # type: ignore
        return mapped_column(
            index=True,
            nullable=False
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
