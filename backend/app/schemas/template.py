"""
Pydantic schemas for template management API.

These schemas handle validation for template creation, updates, and responses.
Templates have a hierarchical structure: Template -> Sections -> Fields.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# Field Schemas
# ============================================================================

class TemplateFieldCreate(BaseModel):
    """Schema for creating a template field."""

    label: str = Field(..., min_length=1, max_length=500)
    field_type: Literal["dropdown", "text"]
    options: list[str] | None = None
    order: int = Field(..., ge=0)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: list[str] | None, info) -> list[str] | None:
        """Ensure options are provided for dropdown fields."""
        field_type = info.data.get("field_type")
        if field_type == "dropdown" and not v:
            raise ValueError("options are required for dropdown field_type")
        return v


class TemplateFieldResponse(BaseModel):
    """Schema for template field response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    field_type: str
    options: list[str] | None
    order: int


# ============================================================================
# Section Schemas
# ============================================================================

class TemplateSectionCreate(BaseModel):
    """Schema for creating a template section."""

    name: str = Field(..., min_length=1, max_length=255)
    fields: list[TemplateFieldCreate]
    order: int = Field(..., ge=0)


class TemplateSectionResponse(BaseModel):
    """Schema for template section response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    order: int
    fields: list[TemplateFieldResponse]


# ============================================================================
# Template Schemas
# ============================================================================

class TemplateCreate(BaseModel):
    """Schema for creating a template."""

    name: str = Field(..., min_length=1, max_length=255)
    category: Literal["Commissioning", "Inspection", "Maintenance", "Testing"]
    sections: list[TemplateSectionCreate]
    title: str | None = Field(None, max_length=500)
    reference_standards: str | None = None
    planning_requirements: str | None = None


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    category: Literal["Commissioning", "Inspection", "Maintenance", "Testing"] | None = None
    is_active: bool | None = None
    title: str | None = Field(None, max_length=500)
    reference_standards: str | None = None
    planning_requirements: str | None = None
    pdf_layout_id: UUID | None = None


class TemplateResponse(BaseModel):
    """Schema for full template response (with sections)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    code: str
    category: str
    version: int
    title: str | None
    reference_standards: str | None
    planning_requirements: str | None
    is_active: bool
    pdf_layout_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
    sections: list[TemplateSectionResponse] | None = None


class TemplateListItem(BaseModel):
    """Schema for template list item (without sections)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    category: str
    version: int
    is_active: bool
    created_at: datetime


class TemplateListResponse(BaseModel):
    """Schema for paginated template list response."""

    templates: list[TemplateListItem]
    total: int


# ============================================================================
# Excel Parse Schemas
# ============================================================================

class ExcelParseResponse(BaseModel):
    """Schema for Excel template parsing response."""

    valid: bool
    sections: list[TemplateSectionCreate] | None = None
    errors: list[str] | None = None
    summary: dict[str, int] | None = None  # e.g., {"section_count": 3, "field_count": 45}
