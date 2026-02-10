"""
Pydantic schemas for Onboarding API.

Covers onboarding status, step updates, and demo template cloning.
"""

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class OnboardingStepStatus(BaseModel):
    """Status of a single onboarding step."""
    key: str
    status: Literal["pending", "completed", "skipped"]
    label: str


class OnboardingStatusResponse(BaseModel):
    """Full onboarding status for a tenant."""
    id: uuid.UUID
    tenant_id: uuid.UUID
    is_completed: bool
    completed_at: Optional[datetime] = None
    current_step: int
    steps: list[OnboardingStepStatus]
    metadata_json: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class StepUpdateRequest(BaseModel):
    """Request to update a step status."""
    action: Literal["complete", "skip"]


class StepUpdateResponse(BaseModel):
    """Response after updating a step."""
    step_key: str
    new_status: str
    is_completed: bool
    current_step: int


class CloneDemoTemplateResponse(BaseModel):
    """Response after cloning the demo template."""
    template_id: uuid.UUID
    template_name: str
    template_code: str
