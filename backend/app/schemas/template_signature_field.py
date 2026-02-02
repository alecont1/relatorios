"""Pydantic schemas for template signature field API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SignatureFieldCreate(BaseModel):
    """Schema for creating a signature field."""

    role_name: str = Field(..., min_length=1, max_length=100)
    required: bool = True


class SignatureFieldUpdate(BaseModel):
    """Schema for updating a signature field."""

    role_name: str | None = Field(None, min_length=1, max_length=100)
    required: bool | None = None


class SignatureFieldResponse(BaseModel):
    """Schema for signature field response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_id: UUID
    role_name: str
    required: bool
    order: int
    created_at: datetime
    updated_at: datetime


class SignatureFieldListResponse(BaseModel):
    """Schema for list of signature fields."""

    signature_fields: list[SignatureFieldResponse]
    total: int


class SignatureFieldReorder(BaseModel):
    """Schema for reordering signature fields."""

    field_ids: list[UUID] = Field(..., min_length=1)
