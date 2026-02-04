"""
Template field configuration endpoints.

Provides:
- PATCH /templates/fields/{field_id}/config - Update field photo/comment configuration
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from app.core.database import get_db
from app.core.deps import require_role, get_tenant_filter
from app.models.user import User
from app.models.template_field import TemplateField
from app.models.template_section import TemplateSection
from app.models.template import Template
from app.schemas.template_field_config import (
    FieldConfigUpdate,
    FieldConfigResponse,
    PhotoConfig,
    CommentConfig,
)


router = APIRouter(prefix="/templates/fields", tags=["template-field-config"])


async def get_field_with_tenant_check(
    field_id: UUID,
    tenant_id: UUID,
    db: AsyncSession
) -> TemplateField:
    """
    Get a template field and verify tenant ownership.

    Joins through TemplateField -> TemplateSection -> Template to check tenant_id.
    """
    result = await db.execute(
        select(TemplateField)
        .join(TemplateSection, TemplateField.section_id == TemplateSection.id)
        .join(Template, TemplateSection.template_id == Template.id)
        .where(TemplateField.id == field_id)
        .where(Template.tenant_id == tenant_id)
    )
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campo nao encontrado"
        )

    return field


def _field_to_config_response(field: TemplateField) -> FieldConfigResponse:
    """Convert TemplateField model to config response schema."""
    photo_config = None
    if field.photo_config:
        photo_config = PhotoConfig(**field.photo_config)

    comment_config = None
    if field.comment_config:
        comment_config = CommentConfig(**field.comment_config)

    return FieldConfigResponse(
        id=field.id,
        label=field.label,
        field_type=field.field_type,
        photo_config=photo_config,
        comment_config=comment_config,
    )


@router.patch("/{field_id}/config", response_model=FieldConfigResponse)
async def update_field_config(
    field_id: UUID,
    config_data: FieldConfigUpdate,
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update photo and comment configuration for a checklist field.

    Uses flag_modified to ensure JSONB mutation tracking for proper persistence.
    """
    # Get field with tenant verification
    field = await get_field_with_tenant_check(field_id, tenant_id, db)

    # Update photo_config if provided
    if config_data.photo_config is not None:
        field.photo_config = config_data.photo_config.model_dump()
        flag_modified(field, 'photo_config')

    # Update comment_config if provided
    if config_data.comment_config is not None:
        field.comment_config = config_data.comment_config.model_dump()
        flag_modified(field, 'comment_config')

    await db.commit()
    await db.refresh(field)

    return _field_to_config_response(field)


@router.get("/{field_id}/config", response_model=FieldConfigResponse)
async def get_field_config(
    field_id: UUID,
    current_user: Annotated[User, Depends(require_role("viewer", "technician", "project_manager", "tenant_admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Get current configuration for a checklist field.
    """
    # Get field with tenant verification
    field = await get_field_with_tenant_check(field_id, tenant_id, db)

    return _field_to_config_response(field)
