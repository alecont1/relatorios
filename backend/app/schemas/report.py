from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReportStatus:
    """Report status constants."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

    ALL = [DRAFT, IN_PROGRESS, COMPLETED, ARCHIVED]


# --- Info Value Schemas ---


class InfoValueCreate(BaseModel):
    """Schema for creating/updating an info field value."""

    info_field_id: UUID | None = None
    field_label: str = Field(..., min_length=1, max_length=255)
    field_type: str = Field(..., min_length=1, max_length=50)
    value: str | None = None


class InfoValueResponse(BaseModel):
    """Schema for info field value response."""

    id: UUID
    report_id: UUID
    info_field_id: UUID | None
    field_label: str
    field_type: str
    value: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Checklist Response Schemas ---


class ChecklistResponseCreate(BaseModel):
    """Schema for creating/updating a checklist response."""

    section_id: UUID | None = None
    field_id: UUID | None = None
    section_name: str = Field(..., min_length=1, max_length=255)
    section_order: int = Field(default=0, ge=0)
    field_label: str = Field(..., min_length=1, max_length=500)
    field_order: int = Field(default=0, ge=0)
    field_type: str = Field(..., min_length=1, max_length=50)
    field_options: str | None = None
    response_value: str | None = None
    comment: str | None = None
    photos: list[dict] = Field(default_factory=list)


class ChecklistResponseResponse(BaseModel):
    """Schema for checklist response response."""

    id: UUID
    report_id: UUID
    section_id: UUID | None
    field_id: UUID | None
    section_name: str
    section_order: int
    field_label: str
    field_order: int
    field_type: str
    field_options: str | None
    response_value: str | None
    comment: str | None
    photos: list[dict] | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Report Schemas ---


class ReportCreate(BaseModel):
    """Schema for creating a new report."""

    template_id: UUID
    project_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    location: str | None = None


class ReportUpdate(BaseModel):
    """Schema for updating a report (saving draft)."""

    title: str | None = Field(None, min_length=1, max_length=255)
    location: str | None = None
    status: str | None = None
    info_values: list[InfoValueCreate] | None = None
    checklist_responses: list[ChecklistResponseCreate] | None = None
    expected_updated_at: datetime | None = Field(
        None,
        description="For optimistic locking: pass the last known updated_at. "
        "If the report was modified since, a 409 Conflict is returned.",
    )


class ReportResponse(BaseModel):
    """Schema for report response (list view)."""

    id: UUID
    tenant_id: UUID
    template_id: UUID
    project_id: UUID
    user_id: UUID
    title: str
    status: str
    location: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    # Include template name from snapshot for display
    template_name: str | None = None
    # Revision fields
    revision_number: int = 0
    parent_report_id: UUID | None = None
    is_latest_revision: bool = True

    model_config = {"from_attributes": True}


class ReportDetailResponse(BaseModel):
    """Schema for detailed report response (single view)."""

    id: UUID
    tenant_id: UUID
    template_id: UUID
    project_id: UUID
    user_id: UUID
    title: str
    status: str
    location: str | None
    template_snapshot: dict
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    info_values: list[InfoValueResponse]
    checklist_responses: list[ChecklistResponseResponse]
    # Revision fields
    revision_number: int = 0
    parent_report_id: UUID | None = None
    revision_notes: str | None = None
    is_latest_revision: bool = True

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    """Schema for paginated report list."""

    reports: list[ReportResponse]
    total: int


# --- Revision Schemas ---


class RevisionCreate(BaseModel):
    """Schema for creating a report revision."""

    revision_notes: str | None = None


class RevisionResponse(BaseModel):
    """Schema for a revision entry in the history list."""

    id: UUID
    revision_number: int
    status: str
    revision_notes: str | None
    parent_report_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RevisionListResponse(BaseModel):
    """Schema for revision history list."""

    revisions: list[RevisionResponse]
    total: int
