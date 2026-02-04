"""
Template info field management endpoints.

Provides:
- POST /templates/{template_id}/info-fields - Create info field
- GET /templates/{template_id}/info-fields - List info fields
- PATCH /templates/{template_id}/info-fields/{field_id} - Update info field
- DELETE /templates/{template_id}/info-fields/{field_id} - Delete info field
- PUT /templates/{template_id}/info-fields/reorder - Reorder info fields
"""

import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role, get_tenant_filter
from app.models.user import User
from app.models.template import Template
from app.models.template_info_field import TemplateInfoField
from app.schemas.template_info_field import (
    InfoFieldCreate,
    InfoFieldUpdate,
    InfoFieldResponse,
    InfoFieldListResponse,
    InfoFieldReorder,
)


router = APIRouter(prefix="/templates", tags=["template-info-fields"])


async def verify_template_ownership(
    template_id: UUID,
    tenant_id: UUID,
    db: AsyncSession
) -> Template:
    """Verify template exists and belongs to tenant."""
    result = await db.execute(
        select(Template)
        .where(Template.id == template_id)
        .where(Template.tenant_id == tenant_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado"
        )

    return template


def _parse_options(options_str: str | None) -> list[str] | None:
    """Parse options JSON string to list."""
    if not options_str:
        return None
    try:
        return json.loads(options_str)
    except (json.JSONDecodeError, TypeError):
        return None


def _info_field_to_response(field: TemplateInfoField) -> InfoFieldResponse:
    """Convert TemplateInfoField model to response schema."""
    return InfoFieldResponse(
        id=field.id,
        template_id=field.template_id,
        label=field.label,
        field_type=field.field_type,
        options=_parse_options(field.options),
        required=field.required,
        order=field.order,
        created_at=field.created_at,
        updated_at=field.updated_at,
    )


@router.post(
    "/{template_id}/info-fields",
    response_model=InfoFieldResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_info_field(
    template_id: UUID,
    field_data: InfoFieldCreate,
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new info field for a template.

    Order is auto-generated as max(order) + 1 for the template.
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get max order for this template
    result = await db.execute(
        select(func.max(TemplateInfoField.order))
        .where(TemplateInfoField.template_id == template_id)
    )
    max_order = result.scalar_one_or_none() or 0

    # Create field
    field = TemplateInfoField(
        template_id=template_id,
        label=field_data.label,
        field_type=field_data.field_type,
        options=json.dumps(field_data.options) if field_data.options else None,
        required=field_data.required,
        order=max_order + 1,
    )
    db.add(field)
    await db.commit()
    await db.refresh(field)

    return _info_field_to_response(field)


@router.get("/{template_id}/info-fields", response_model=InfoFieldListResponse)
async def list_info_fields(
    template_id: UUID,
    current_user: Annotated[User, Depends(require_role("viewer", "technician", "project_manager", "tenant_admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    List all info fields for a template, ordered by order field.
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get all info fields ordered
    result = await db.execute(
        select(TemplateInfoField)
        .where(TemplateInfoField.template_id == template_id)
        .order_by(TemplateInfoField.order.asc())
    )
    fields = result.scalars().all()

    return InfoFieldListResponse(
        info_fields=[_info_field_to_response(f) for f in fields],
        total=len(fields)
    )


@router.patch(
    "/{template_id}/info-fields/{field_id}",
    response_model=InfoFieldResponse
)
async def update_info_field(
    template_id: UUID,
    field_id: UUID,
    field_data: InfoFieldUpdate,
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update an info field.

    Can update label, field_type, options, and required flag.
    When changing to/from select type, validates options accordingly.
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get field
    result = await db.execute(
        select(TemplateInfoField)
        .where(TemplateInfoField.id == field_id)
        .where(TemplateInfoField.template_id == template_id)
    )
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campo de informacao nao encontrado"
        )

    # Update fields
    if field_data.label is not None:
        field.label = field_data.label

    if field_data.field_type is not None:
        # Validate options when changing field_type
        new_type = field_data.field_type
        new_options = field_data.options if field_data.options is not None else _parse_options(field.options)

        if new_type == "select" and not new_options:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="options are required for select field_type"
            )

        field.field_type = new_type

    if field_data.options is not None:
        # Validate options for current or new field_type
        current_type = field.field_type
        if current_type != "select" and field_data.options:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="options only allowed for select field_type"
            )
        field.options = json.dumps(field_data.options) if field_data.options else None

    if field_data.required is not None:
        field.required = field_data.required

    await db.commit()
    await db.refresh(field)

    return _info_field_to_response(field)


@router.delete(
    "/{template_id}/info-fields/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_info_field(
    template_id: UUID,
    field_id: UUID,
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an info field.
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get field
    result = await db.execute(
        select(TemplateInfoField)
        .where(TemplateInfoField.id == field_id)
        .where(TemplateInfoField.template_id == template_id)
    )
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campo de informacao nao encontrado"
        )

    await db.delete(field)
    await db.commit()


@router.put("/{template_id}/info-fields/reorder", response_model=InfoFieldListResponse)
async def reorder_info_fields(
    template_id: UUID,
    reorder_data: InfoFieldReorder,
    current_user: Annotated[User, Depends(require_role("tenant_admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Reorder info fields.

    Accepts list of field_ids in desired order.
    All IDs must belong to this template.
    Updates order field for each (1, 2, 3...).
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get all fields for this template
    result = await db.execute(
        select(TemplateInfoField)
        .where(TemplateInfoField.template_id == template_id)
    )
    fields = {f.id: f for f in result.scalars().all()}

    # Verify all IDs belong to this template
    for field_id in reorder_data.field_ids:
        if field_id not in fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campo {field_id} nao pertence a este template"
            )

    # Update order for each field
    for idx, field_id in enumerate(reorder_data.field_ids, start=1):
        fields[field_id].order = idx

    await db.commit()

    # Return updated list
    result = await db.execute(
        select(TemplateInfoField)
        .where(TemplateInfoField.template_id == template_id)
        .order_by(TemplateInfoField.order.asc())
    )
    updated_fields = result.scalars().all()

    return InfoFieldListResponse(
        info_fields=[_info_field_to_response(f) for f in updated_fields],
        total=len(updated_fields)
    )
