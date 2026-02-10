"""
Tenant Pydantic schemas.

Provides validation and serialization for tenant CRUD operations.
"""
import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TenantBase(BaseModel):
    """Base tenant schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Tenant organization name")
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$", description="Unique slug for tenant")
    is_active: bool = Field(default=True, description="Whether tenant is active")


class TenantCreate(TenantBase):
    """Schema for creating a new tenant."""
    pass


class TenantUpdate(BaseModel):
    """Schema for updating tenant basic info."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    is_active: Optional[bool] = None


class WatermarkConfig(BaseModel):
    """Configuration for which fields appear in photo watermarks."""
    logo: bool = True
    gps: bool = True
    datetime: bool = True
    company_name: bool = True
    report_number: bool = False
    technician_name: bool = True


class TenantBrandingUpdate(BaseModel):
    """Schema for updating tenant branding and contact information."""

    # Branding fields
    logo_primary_key: Optional[str] = Field(None, max_length=500, description="R2 object key for primary logo")
    logo_secondary_key: Optional[str] = Field(None, max_length=500, description="R2 object key for secondary logo")
    brand_color_primary: Optional[str] = Field(None, description="Primary brand color in hex format #RRGGBB")
    brand_color_secondary: Optional[str] = Field(None, description="Secondary brand color in hex format #RRGGBB")
    brand_color_accent: Optional[str] = Field(None, description="Accent brand color in hex format #RRGGBB")

    # Contact fields
    contact_address: Optional[str] = Field(None, max_length=500, description="Physical address")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    contact_email: Optional[str] = Field(None, max_length=255, description="Contact email address")
    contact_website: Optional[str] = Field(None, max_length=255, description="Website URL")

    # Watermark fields
    watermark_text: Optional[str] = Field(None, max_length=255, description="Watermark text for reports")
    watermark_config: Optional[dict] = Field(None, description="Watermark field configuration")

    @field_validator("brand_color_primary", "brand_color_secondary", "brand_color_accent")
    @classmethod
    def validate_hex_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color format #RRGGBB."""
        if v is None:
            return v

        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be in hex format #RRGGBB (e.g., #FF5733)")

        return v.upper()  # Normalize to uppercase


class TenantResponse(TenantBase):
    """Schema for tenant response with all fields."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Branding fields
    logo_primary_key: Optional[str] = None
    logo_secondary_key: Optional[str] = None
    brand_color_primary: Optional[str] = None
    brand_color_secondary: Optional[str] = None
    brand_color_accent: Optional[str] = None

    # Contact fields
    contact_address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    contact_website: Optional[str] = None

    # Watermark fields
    watermark_text: Optional[str] = None
    watermark_config: Optional[dict] = None

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Schema for paginated tenant list response."""

    tenants: list[TenantResponse]
    total: int
