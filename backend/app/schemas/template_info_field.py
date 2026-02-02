"""Pydantic schemas for template info field API."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InfoFieldCreate(BaseModel):
    """Schema for creating an info field."""
    label: str = Field(..., min_length=1, max_length=255)
    field_type: Literal["text", "date", "select"]
    options: list[str] | None = None
    required: bool = True

    @field_validator("options")
    @classmethod
    def validate_options(cls, v, info):
        """Ensure options provided for select type."""
        field_type = info.data.get("field_type")
        if field_type == "select" and not v:
            raise ValueError("options are required for select field_type")
        if field_type != "select" and v:
            raise ValueError("options only allowed for select field_type")
        return v


class InfoFieldUpdate(BaseModel):
    """Schema for updating an info field."""
    label: str | None = Field(None, min_length=1, max_length=255)
    field_type: Literal["text", "date", "select"] | None = None
    options: list[str] | None = None
    required: bool | None = None


class InfoFieldResponse(BaseModel):
    """Schema for info field response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_id: UUID
    label: str
    field_type: str
    options: list[str] | None
    required: bool
    order: int
    created_at: datetime
    updated_at: datetime


class InfoFieldListResponse(BaseModel):
    """Schema for list of info fields."""
    info_fields: list[InfoFieldResponse]
    total: int


class InfoFieldReorder(BaseModel):
    """Schema for reordering info fields."""
    field_ids: list[UUID] = Field(..., min_length=1)
