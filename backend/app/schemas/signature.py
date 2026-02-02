"""Pydantic schemas for report signatures."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SignatureCreate(BaseModel):
    """Schema for creating a signature (metadata only, file uploaded separately)."""

    role_name: str = Field(..., max_length=100)
    signer_name: str | None = Field(None, max_length=255)
    signature_field_id: UUID | None = None


class SignatureResponse(BaseModel):
    """Schema for signature response."""

    id: UUID
    role_name: str
    signer_name: str | None
    url: str  # Presigned URL for the signature image
    signed_at: datetime
    signature_field_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SignatureListResponse(BaseModel):
    """Schema for list of signatures."""

    signatures: list[SignatureResponse]
    total: int
