"""
Template management endpoints.

Provides:
- POST /templates/parse - Parse Excel file and return preview
- POST /templates - Create template from validated data
- GET /templates - List templates with search/filter
- GET /templates/{id} - Get template with sections/fields
- PATCH /templates/{id} - Update template metadata
"""

import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import require_role, get_tenant_filter
from app.models.user import User
from app.models.template import Template
from app.models.template_section import TemplateSection
from app.models.template_field import TemplateField
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListItem,
    TemplateListResponse,
    ExcelParseResponse,
    TemplateSectionCreate,
    TemplateFieldCreate,
    TemplateSectionResponse,
    TemplateFieldResponse,
)
from app.services.excel_parser import parse_template_excel


router = APIRouter(prefix="/templates", tags=["templates"])


# Code generation helper
async def generate_template_code(db: AsyncSession, tenant_id: UUID, category: str) -> str:
    """Generate next template code like COM-001, INS-002."""
    prefix_map = {
        "Commissioning": "COM",
        "Inspection": "INS",
        "Maintenance": "MNT",
        "Testing": "TST",
    }
    prefix = prefix_map.get(category, "TPL")

    # Get max code for this category in tenant
    result = await db.execute(
        select(Template.code)
        .where(Template.tenant_id == tenant_id)
        .where(Template.code.like(f"{prefix}-%"))
        .order_by(Template.code.desc())
        .limit(1)
    )
    max_code = result.scalar_one_or_none()

    if max_code:
        try:
            seq = int(max_code.split("-")[1]) + 1
        except (IndexError, ValueError):
            seq = 1
    else:
        seq = 1

    return f"{prefix}-{seq:03d}"


def _template_to_response(template: Template) -> TemplateResponse:
    """Convert Template model to response schema with parsed options."""
    sections = []
    for section in template.sections:
        fields = []
        for field in section.fields:
            options = json.loads(field.options) if field.options else None
            fields.append(TemplateFieldResponse(
                id=field.id,
                label=field.label,
                field_type=field.field_type,
                options=options,
                order=field.order,
            ))
        sections.append(TemplateSectionResponse(
            id=section.id,
            name=section.name,
            order=section.order,
            fields=fields,
        ))

    return TemplateResponse(
        id=template.id,
        tenant_id=template.tenant_id,
        name=template.name,
        code=template.code,
        category=template.category,
        version=template.version,
        title=template.title,
        reference_standards=template.reference_standards,
        planning_requirements=template.planning_requirements,
        is_active=template.is_active,
        created_at=template.created_at,
        updated_at=template.updated_at,
        sections=sections,
    )


@router.post("/parse", response_model=ExcelParseResponse)
async def parse_excel_template(
    file: UploadFile = File(...),
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))] = None,
):
    """
    Parse uploaded Excel file and return preview.

    Does NOT save to database - just validates and returns parsed structure.
    Admin must confirm before actual creation via POST /templates.

    Expected Excel format:
    | Section | Script Step | Result Type | Step Result Values |
    """
    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser Excel (.xlsx ou .xls)"
        )

    # Read file content
    content = await file.read()

    # Parse Excel
    result = parse_template_excel(content)

    if not result.valid:
        return ExcelParseResponse(
            valid=False,
            errors=result.errors
        )

    # Convert to schema format
    sections = []
    for section in result.sections or []:
        fields = [
            TemplateFieldCreate(
                label=f.label,
                field_type=f.field_type,
                options=f.options,
                order=f.order
            )
            for f in section.fields
        ]
        sections.append(TemplateSectionCreate(
            name=section.name,
            order=section.order,
            fields=fields
        ))

    return ExcelParseResponse(
        valid=True,
        sections=sections,
        summary=result.summary
    )


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new template from validated data.

    Code is auto-generated based on category (COM-001, INS-002, etc.).
    Sections and fields are created in a single transaction.
    """
    # Generate code
    code = await generate_template_code(db, tenant_id, template_data.category)

    # Create template
    template = Template(
        tenant_id=tenant_id,
        name=template_data.name,
        code=code,
        category=template_data.category,
        version=1,
        title=template_data.title,
        reference_standards=template_data.reference_standards,
        planning_requirements=template_data.planning_requirements,
        is_active=True,
    )
    db.add(template)
    await db.flush()  # Get template.id

    # Create sections and fields
    for section_data in template_data.sections:
        section = TemplateSection(
            template_id=template.id,
            name=section_data.name,
            order=section_data.order,
        )
        db.add(section)
        await db.flush()  # Get section.id

        for field_data in section_data.fields:
            # Default configurations for photo and comment
            default_photo_config = {
                "required": False,
                "min_count": 0,
                "max_count": 5,
                "require_gps": False,
                "watermark": True,
            }
            default_comment_config = {
                "enabled": True,
                "required": False,
            }

            field = TemplateField(
                section_id=section.id,
                label=field_data.label,
                field_type=field_data.field_type,
                options=json.dumps(field_data.options) if field_data.options else None,
                order=field_data.order,
                photo_config=default_photo_config,
                comment_config=default_comment_config,
            )
            db.add(field)

    await db.commit()

    # Refresh with relationships
    await db.refresh(template)
    result = await db.execute(
        select(Template)
        .where(Template.id == template.id)
        .options(
            selectinload(Template.sections).selectinload(TemplateSection.fields)
        )
    )
    template = result.scalar_one()

    return _template_to_response(template)


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    current_user: Annotated[User, Depends(require_role("user", "manager", "admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
    search: str = Query("", description="Search by name or code"),
    status: str = Query("active", description="Filter by status: all, active, inactive"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    List templates for current tenant.

    Regular users only see active templates.
    Admins can filter by status (all, active, inactive).
    """
    query = select(Template).where(Template.tenant_id == tenant_id)

    # Search filter
    if search:
        query = query.where(
            or_(
                Template.name.ilike(f"%{search}%"),
                Template.code.ilike(f"%{search}%")
            )
        )

    # Status filter - regular users always see only active
    if current_user.role in ["user", "manager"]:
        query = query.where(Template.is_active == True)
    elif status == "active":
        query = query.where(Template.is_active == True)
    elif status == "inactive":
        query = query.where(Template.is_active == False)
    # "all" shows both

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Get paginated results
    query = query.order_by(Template.name.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    templates = result.scalars().all()

    items = [
        TemplateListItem(
            id=t.id,
            name=t.name,
            code=t.code,
            category=t.category,
            version=t.version,
            is_active=t.is_active,
            created_at=t.created_at,
        )
        for t in templates
    ]

    return TemplateListResponse(templates=items, total=total)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    current_user: Annotated[User, Depends(require_role("user", "manager", "admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """Get a single template with all sections and fields."""
    result = await db.execute(
        select(Template)
        .where(Template.id == template_id)
        .where(Template.tenant_id == tenant_id)
        .options(
            selectinload(Template.sections).selectinload(TemplateSection.fields)
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado"
        )

    # Regular users can't see inactive templates
    if not template.is_active and current_user.role in ["user", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado"
        )

    return _template_to_response(template)


@router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    template_data: TemplateUpdate,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
):
    """
    Update template metadata.

    Only name, category, is_active, and header fields can be updated.
    Code cannot be changed after creation.
    """
    result = await db.execute(
        select(Template)
        .where(Template.id == template_id)
        .where(Template.tenant_id == tenant_id)
        .options(
            selectinload(Template.sections).selectinload(TemplateSection.fields)
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado"
        )

    # Update allowed fields
    if template_data.name is not None:
        template.name = template_data.name
    if template_data.category is not None:
        template.category = template_data.category
    if template_data.is_active is not None:
        template.is_active = template_data.is_active
    if template_data.title is not None:
        template.title = template_data.title
    if template_data.reference_standards is not None:
        template.reference_standards = template_data.reference_standards
    if template_data.planning_requirements is not None:
        template.planning_requirements = template_data.planning_requirements

    await db.commit()
    await db.refresh(template)

    return _template_to_response(template)
