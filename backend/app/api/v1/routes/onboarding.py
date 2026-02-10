"""
Onboarding API endpoints for tenant guided setup wizard.

Provides endpoints for checking onboarding status, updating step progress,
and cloning demo templates. Accessible by tenant_admin and superadmin.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_tenant_admin
from app.models.user import User
from app.schemas.onboarding import (
    CloneDemoTemplateResponse,
    OnboardingStatusResponse,
    OnboardingStepStatus,
    StepUpdateRequest,
    StepUpdateResponse,
)
from app.services.onboarding import STEP_LABELS, onboarding_service

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


def _get_tenant_id(user: User) -> UUID:
    """Extract tenant_id from user, raising 400 if not available."""
    if user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin deve especificar tenant_id",
        )
    return user.tenant_id


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    current_user: Annotated[User, Depends(require_tenant_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Get onboarding status for the current tenant."""
    tenant_id = _get_tenant_id(current_user)
    data = await onboarding_service.get_status(db, tenant_id)

    return OnboardingStatusResponse(
        id=data["id"],
        tenant_id=data["tenant_id"],
        is_completed=data["is_completed"],
        completed_at=data["completed_at"],
        current_step=data["current_step"],
        steps=[OnboardingStepStatus(**s) for s in data["steps"]],
        metadata_json=data["metadata_json"],
    )


@router.put("/step/{step_key}", response_model=StepUpdateResponse)
async def update_step(
    step_key: str,
    body: StepUpdateRequest,
    current_user: Annotated[User, Depends(require_tenant_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Complete or skip an onboarding step."""
    tenant_id = _get_tenant_id(current_user)

    try:
        if body.action == "complete":
            onboarding = await onboarding_service.complete_step(db, tenant_id, step_key)
        else:
            onboarding = await onboarding_service.skip_step(db, tenant_id, step_key)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    attr = f"step_{step_key}"
    return StepUpdateResponse(
        step_key=step_key,
        new_status=getattr(onboarding, attr),
        is_completed=onboarding.is_completed,
        current_step=onboarding.current_step,
    )


@router.post(
    "/clone-demo-template",
    response_model=CloneDemoTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def clone_demo_template(
    current_user: Annotated[User, Depends(require_tenant_admin)],
    db: AsyncSession = Depends(get_db),
):
    """Clone the demo template into the current tenant."""
    tenant_id = _get_tenant_id(current_user)
    template = await onboarding_service.clone_demo_template(db, tenant_id)

    return CloneDemoTemplateResponse(
        template_id=template.id,
        template_name=template.name,
        template_code=template.code,
    )
