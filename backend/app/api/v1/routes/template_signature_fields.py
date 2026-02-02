"""
Template signature field management endpoints.

Provides:
- POST /templates/{template_id}/signature-fields - Create signature field
- GET /templates/{template_id}/signature-fields - List signature fields
- PATCH /templates/{template_id}/signature-fields/{field_id} - Update signature field
- DELETE /templates/{template_id}/signature-fields/{field_id} - Delete signature field
- PUT /templates/{template_id}/signature-fields/reorder - Reorder signature fields
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role, get_tenant_filter
from app.models.user import User
from app.models.template import Template
from app.models.template_signature_field import TemplateSignatureField
from app.schemas.template_signature_field import (
    SignatureFieldCreate,
    SignatureFieldUpdate,
    SignatureFieldResponse,
    SignatureFieldListResponse,
    SignatureFieldReorder,
)


router = APIRouter(prefix="/templates", tags=["template-signature-fields"])


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


def _signature_field_to_response(field: TemplateSignatureField) -> SignatureFieldResponse:
    """Convert TemplateSignatureField model to response schema."""
    return SignatureFieldResponse(
        id=field.id,
        template_id=field.template_id,
        role_name=field.role_name,
        required=field.required,
        order=field.order,
        created_at=field.created_at,
        updated_at=field.updated_at,
    )


@router.post(
    "/{template_id}/signature-fields",
    response_model=SignatureFieldResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_signature_field(
    template_id: UUID,
    field_data: SignatureFieldCreate,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new signature field for a template.

    Order is auto-generated as max(order) + 1 for the template.
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get max order for this template
    result = await db.execute(
        select(func.max(TemplateSignatureField.order))
        .where(TemplateSignatureField.template_id == template_id)
    )
    max_order = result.scalar_one_or_none() or 0

    # Create field
    field = TemplateSignatureField(
        template_id=template_id,
        role_name=field_data.role_name,
        required=field_data.required,
        order=max_order + 1,
    )
    db.add(field)
    await db.commit()
    await db.refresh(field)

    return _signature_field_to_response(field)


@router.get("/{template_id}/signature-fields", response_model=SignatureFieldListResponse)
async def list_signature_fields(
    template_id: UUID,
    current_user: Annotated[User, Depends(require_role("user", "manager", "admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    List all signature fields for a template, ordered by order field.
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get all signature fields ordered
    result = await db.execute(
        select(TemplateSignatureField)
        .where(TemplateSignatureField.template_id == template_id)
        .order_by(TemplateSignatureField.order.asc())
    )
    fields = result.scalars().all()

    return SignatureFieldListResponse(
        signature_fields=[_signature_field_to_response(f) for f in fields],
        total=len(fields)
    )


@router.patch(
    "/{template_id}/signature-fields/{field_id}",
    response_model=SignatureFieldResponse
)
async def update_signature_field(
    template_id: UUID,
    field_id: UUID,
    field_data: SignatureFieldUpdate,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update a signature field.

    Can update role_name and required flag.
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get field
    result = await db.execute(
        select(TemplateSignatureField)
        .where(TemplateSignatureField.id == field_id)
        .where(TemplateSignatureField.template_id == template_id)
    )
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campo de assinatura nao encontrado"
        )

    # Update fields
    if field_data.role_name is not None:
        field.role_name = field_data.role_name

    if field_data.required is not None:
        field.required = field_data.required

    await db.commit()
    await db.refresh(field)

    return _signature_field_to_response(field)


@router.delete(
    "/{template_id}/signature-fields/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_signature_field(
    template_id: UUID,
    field_id: UUID,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a signature field.
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get field
    result = await db.execute(
        select(TemplateSignatureField)
        .where(TemplateSignatureField.id == field_id)
        .where(TemplateSignatureField.template_id == template_id)
    )
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campo de assinatura nao encontrado"
        )

    await db.delete(field)
    await db.commit()


@router.put("/{template_id}/signature-fields/reorder", response_model=SignatureFieldListResponse)
async def reorder_signature_fields(
    template_id: UUID,
    reorder_data: SignatureFieldReorder,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Reorder signature fields.

    Accepts list of field_ids in desired order.
    All IDs must belong to this template.
    Updates order field for each (1, 2, 3...).
    """
    # Verify template exists and belongs to tenant
    await verify_template_ownership(template_id, tenant_id, db)

    # Get all fields for this template
    result = await db.execute(
        select(TemplateSignatureField)
        .where(TemplateSignatureField.template_id == template_id)
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
        select(TemplateSignatureField)
        .where(TemplateSignatureField.template_id == template_id)
        .order_by(TemplateSignatureField.order.asc())
    )
    updated_fields = result.scalars().all()

    return SignatureFieldListResponse(
        signature_fields=[_signature_field_to_response(f) for f in updated_fields],
        total=len(updated_fields)
    )
