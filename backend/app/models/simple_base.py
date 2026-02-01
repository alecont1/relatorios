import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class SimpleBase(DeclarativeBase):
    """
    Simple base model for child tables that don't need tenant_id.

    Used for models that inherit tenant isolation through their parent
    (e.g., TemplateSection belongs to Template which has tenant_id).

    Provides:
    - id: Primary key (UUID)
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update
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
