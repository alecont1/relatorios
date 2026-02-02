"""Pydantic schemas for checklist field configuration."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PhotoConfig(BaseModel):
    """Photo configuration for a checklist field."""

    required: bool = False
    min_count: int = Field(default=0, ge=0)
    max_count: int = Field(default=10, ge=1, le=20)
    require_gps: bool = False
    watermark: bool = True

    @model_validator(mode="after")
    def validate_counts(self):
        """Ensure min_count does not exceed max_count."""
        if self.min_count > self.max_count:
            raise ValueError("min_count cannot exceed max_count")
        return self


class CommentConfig(BaseModel):
    """Comment configuration for a checklist field."""

    enabled: bool = True
    required: bool = False


class FieldConfigUpdate(BaseModel):
    """Schema for updating field configuration."""

    photo_config: PhotoConfig | None = None
    comment_config: CommentConfig | None = None


class FieldConfigResponse(BaseModel):
    """Schema for field with configuration."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    field_type: str
    photo_config: PhotoConfig | None
    comment_config: CommentConfig | None
