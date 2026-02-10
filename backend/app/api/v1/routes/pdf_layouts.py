"""
PDF Layout API endpoints.

Provides CRUD operations for PDF layouts:
- List available layouts (system + custom for tenant)
- Get layout details
- Create custom layout (Enterprise only)
- Update custom layout (Enterprise only)
- Delete custom layout (Enterprise only)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_tenant_filter
from app.models.pdf_layout import PdfLayout
from app.models.user import User
from app.schemas.pdf_layout import (
    PdfLayoutCreate,
    PdfLayoutUpdate,
    PdfLayoutResponse,
    PdfLayoutListResponse,
)
from app.services.feature_check import check_feature

router = APIRouter(prefix="/pdf-layouts", tags=["pdf-layouts"])


@router.get("/", response_model=PdfLayoutListResponse)
async def list_pdf_layouts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    List available PDF layouts.

    Returns system layouts (available to all) plus custom layouts
    belonging to the current tenant.
    """
    conditions = [PdfLayout.is_active == True]

    if tenant_id is not None:
        # System layouts (no tenant) + this tenant's custom layouts
        conditions.append(
            or_(
                PdfLayout.tenant_id.is_(None),
                PdfLayout.tenant_id == tenant_id,
            )
        )

    result = await db.execute(
        select(PdfLayout)
        .where(and_(*conditions))
        .order_by(PdfLayout.is_system.desc(), PdfLayout.name)
    )
    layouts = list(result.scalars().all())

    return PdfLayoutListResponse(layouts=layouts, total=len(layouts))


@router.get("/{layout_id}", response_model=PdfLayoutResponse)
async def get_pdf_layout(
    layout_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """Get a PDF layout by ID."""
    conditions = [PdfLayout.id == layout_id]

    if tenant_id is not None:
        conditions.append(
            or_(
                PdfLayout.tenant_id.is_(None),
                PdfLayout.tenant_id == tenant_id,
            )
        )

    result = await db.execute(
        select(PdfLayout).where(and_(*conditions))
    )
    layout = result.scalar_one_or_none()

    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout nao encontrado",
        )

    return layout


@router.post("/", response_model=PdfLayoutResponse, status_code=status.HTTP_201_CREATED)
async def create_pdf_layout(
    data: PdfLayoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Create a custom PDF layout.

    Requires Enterprise plan with custom_pdf feature enabled.
    """
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin deve especificar tenant_id na query",
        )

    # Check feature flag
    has_feature = await check_feature(db, tenant_id, "custom_pdf")
    if not has_feature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recurso custom_pdf nao disponivel no plano atual",
        )

    # Check slug uniqueness for this tenant
    existing = await db.execute(
        select(PdfLayout).where(
            and_(
                PdfLayout.tenant_id == tenant_id,
                PdfLayout.slug == data.slug,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ja existe um layout com slug '{data.slug}' para este tenant",
        )

    layout = PdfLayout(
        tenant_id=tenant_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        config_json=data.config_json,
        is_system=False,
        is_active=data.is_active,
    )
    db.add(layout)
    await db.commit()
    await db.refresh(layout)

    return layout


@router.patch("/{layout_id}", response_model=PdfLayoutResponse)
async def update_pdf_layout(
    layout_id: UUID,
    data: PdfLayoutUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Update a custom PDF layout.

    Cannot update system layouts. Requires custom_pdf feature.
    """
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin deve especificar tenant_id na query",
        )

    has_feature = await check_feature(db, tenant_id, "custom_pdf")
    if not has_feature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recurso custom_pdf nao disponivel no plano atual",
        )

    result = await db.execute(
        select(PdfLayout).where(
            and_(
                PdfLayout.id == layout_id,
                PdfLayout.tenant_id == tenant_id,
                PdfLayout.is_system == False,
            )
        )
    )
    layout = result.scalar_one_or_none()

    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout customizado nao encontrado",
        )

    if data.name is not None:
        layout.name = data.name
    if data.slug is not None:
        # Check slug uniqueness
        existing = await db.execute(
            select(PdfLayout).where(
                and_(
                    PdfLayout.tenant_id == tenant_id,
                    PdfLayout.slug == data.slug,
                    PdfLayout.id != layout_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ja existe um layout com slug '{data.slug}' para este tenant",
            )
        layout.slug = data.slug
    if data.description is not None:
        layout.description = data.description
    if data.config_json is not None:
        layout.config_json = data.config_json
    if data.is_active is not None:
        layout.is_active = data.is_active

    await db.commit()
    await db.refresh(layout)

    return layout


@router.delete("/{layout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf_layout(
    layout_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Delete a custom PDF layout.

    Cannot delete system layouts. Requires custom_pdf feature.
    """
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin deve especificar tenant_id na query",
        )

    has_feature = await check_feature(db, tenant_id, "custom_pdf")
    if not has_feature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recurso custom_pdf nao disponivel no plano atual",
        )

    result = await db.execute(
        select(PdfLayout).where(
            and_(
                PdfLayout.id == layout_id,
                PdfLayout.tenant_id == tenant_id,
                PdfLayout.is_system == False,
            )
        )
    )
    layout = result.scalar_one_or_none()

    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout customizado nao encontrado",
        )

    await db.delete(layout)
    await db.commit()
