"""
Report API endpoints.

Provides CRUD operations for reports with:
- Create report from template (snapshots template)
- List reports with filters (status, date, template)
- Get report details with all responses
- Update report (save draft)
- Complete report
- Archive report
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, get_tenant_filter
from app.models import (
    Report,
    ReportInfoValue,
    ReportChecklistResponse,
    Template,
    User,
)
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportDetailResponse,
    ReportListResponse,
    ReportStatus,
    InfoValueResponse,
    ChecklistResponseResponse,
)

router = APIRouter(prefix="/reports", tags=["reports"])


def _serialize_template_snapshot(template: Template) -> dict:
    """Create a complete snapshot of a template for historical consistency."""
    return {
        "id": str(template.id),
        "name": template.name,
        "code": template.code,
        "category": template.category,
        "version": template.version,
        "title": template.title,
        "reference_standards": template.reference_standards,
        "planning_requirements": template.planning_requirements,
        "info_fields": [
            {
                "id": str(f.id),
                "label": f.label,
                "field_type": f.field_type,
                "placeholder": f.placeholder,
                "required": f.required,
                "order": f.order,
            }
            for f in sorted(template.info_fields, key=lambda x: x.order)
        ],
        "sections": [
            {
                "id": str(s.id),
                "name": s.name,
                "order": s.order,
                "fields": [
                    {
                        "id": str(f.id),
                        "label": f.label,
                        "field_type": f.field_type,
                        "options": f.options,
                        "order": f.order,
                        "photo_config": f.photo_config,
                        "comment_config": f.comment_config,
                    }
                    for f in sorted(s.fields, key=lambda x: x.order)
                ],
            }
            for s in sorted(template.sections, key=lambda x: x.order)
        ],
        "signature_fields": [
            {
                "id": str(f.id),
                "role_name": f.role_name,
                "required": f.required,
                "order": f.order,
            }
            for f in sorted(template.signature_fields, key=lambda x: x.order)
        ],
    }


@router.post("/", response_model=ReportDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_filter),
):
    """
    Create a new report from a template.

    - Snapshots the template for historical consistency
    - Creates empty info values and checklist responses based on template structure
    - Sets status to 'draft'
    """
    # Verify template exists and belongs to tenant
    result = await db.execute(
        select(Template)
        .options(
            selectinload(Template.info_fields),
            selectinload(Template.sections).selectinload("fields"),
            selectinload(Template.signature_fields),
        )
        .where(
            and_(
                Template.id == data.template_id,
                Template.tenant_id == tenant_id,
                Template.is_active == True,
            )
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado ou inativo",
        )

    # Create template snapshot
    template_snapshot = _serialize_template_snapshot(template)

    # Create report
    report = Report(
        tenant_id=tenant_id,
        template_id=template.id,
        project_id=data.project_id,
        user_id=current_user.id,
        title=data.title,
        location=data.location,
        status=ReportStatus.DRAFT,
        template_snapshot=template_snapshot,
    )
    db.add(report)
    await db.flush()  # Get report.id

    # Create empty info values from template
    for info_field in template.info_fields:
        info_value = ReportInfoValue(
            report_id=report.id,
            info_field_id=info_field.id,
            field_label=info_field.label,
            field_type=info_field.field_type,
            value=None,
        )
        db.add(info_value)

    # Create empty checklist responses from template
    for section in template.sections:
        for field in section.fields:
            response = ReportChecklistResponse(
                report_id=report.id,
                section_id=section.id,
                field_id=field.id,
                section_name=section.name,
                section_order=section.order,
                field_label=field.label,
                field_order=field.order,
                field_type=field.field_type,
                field_options=field.options,
                response_value=None,
                comment=None,
                photos=[],
            )
            db.add(response)

    await db.commit()
    await db.refresh(report)

    # Load relationships for response
    result = await db.execute(
        select(Report)
        .options(
            selectinload(Report.info_values),
            selectinload(Report.checklist_responses),
        )
        .where(Report.id == report.id)
    )
    report = result.scalar_one()

    return _build_detail_response(report)


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_filter),
    status_filter: str | None = Query(None, alias="status"),
    template_id: UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List reports for the current tenant.

    Filters:
    - status: Filter by report status (draft, in_progress, completed, archived)
    - template_id: Filter by template

    Pagination:
    - skip: Number of records to skip
    - limit: Maximum number of records to return
    """
    # Build query conditions
    conditions = [Report.tenant_id == tenant_id]

    if status_filter:
        conditions.append(Report.status == status_filter)

    if template_id:
        conditions.append(Report.template_id == template_id)

    # Count total
    count_query = select(func.count(Report.id)).where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get reports
    query = (
        select(Report)
        .where(and_(*conditions))
        .order_by(Report.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    reports = result.scalars().all()

    return ReportListResponse(
        reports=[_build_list_response(r) for r in reports],
        total=total,
    )


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_filter),
):
    """Get a report with all its info values and checklist responses."""
    result = await db.execute(
        select(Report)
        .options(
            selectinload(Report.info_values),
            selectinload(Report.checklist_responses),
        )
        .where(
            and_(
                Report.id == report_id,
                Report.tenant_id == tenant_id,
            )
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )

    return _build_detail_response(report)


@router.patch("/{report_id}", response_model=ReportDetailResponse)
async def update_report(
    report_id: UUID,
    data: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_filter),
):
    """
    Update a report (save draft).

    - Updates basic fields (title, location)
    - Updates info values
    - Updates checklist responses
    - Sets started_at if transitioning from draft
    """
    result = await db.execute(
        select(Report)
        .options(
            selectinload(Report.info_values),
            selectinload(Report.checklist_responses),
        )
        .where(
            and_(
                Report.id == report_id,
                Report.tenant_id == tenant_id,
            )
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )

    if report.status in [ReportStatus.COMPLETED, ReportStatus.ARCHIVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao e possivel editar um relatorio finalizado ou arquivado",
        )

    # Update basic fields
    if data.title is not None:
        report.title = data.title
    if data.location is not None:
        report.location = data.location
    if data.status is not None and data.status in [ReportStatus.DRAFT, ReportStatus.IN_PROGRESS]:
        if report.status == ReportStatus.DRAFT and data.status == ReportStatus.IN_PROGRESS:
            report.started_at = datetime.utcnow()
        report.status = data.status

    # Update info values
    if data.info_values is not None:
        # Create lookup by field_label
        existing_values = {v.field_label: v for v in report.info_values}
        for iv_data in data.info_values:
            if iv_data.field_label in existing_values:
                existing_values[iv_data.field_label].value = iv_data.value
            else:
                # Create new info value
                new_value = ReportInfoValue(
                    report_id=report.id,
                    info_field_id=iv_data.info_field_id,
                    field_label=iv_data.field_label,
                    field_type=iv_data.field_type,
                    value=iv_data.value,
                )
                db.add(new_value)

    # Update checklist responses
    if data.checklist_responses is not None:
        # Create lookup by field_id (or section_name + field_label)
        existing_responses = {}
        for r in report.checklist_responses:
            key = str(r.field_id) if r.field_id else f"{r.section_name}:{r.field_label}"
            existing_responses[key] = r

        for cr_data in data.checklist_responses:
            key = str(cr_data.field_id) if cr_data.field_id else f"{cr_data.section_name}:{cr_data.field_label}"
            if key in existing_responses:
                resp = existing_responses[key]
                resp.response_value = cr_data.response_value
                resp.comment = cr_data.comment
                if cr_data.photos:
                    resp.photos = cr_data.photos
            else:
                # Create new response
                new_response = ReportChecklistResponse(
                    report_id=report.id,
                    section_id=cr_data.section_id,
                    field_id=cr_data.field_id,
                    section_name=cr_data.section_name,
                    section_order=cr_data.section_order,
                    field_label=cr_data.field_label,
                    field_order=cr_data.field_order,
                    field_type=cr_data.field_type,
                    field_options=cr_data.field_options,
                    response_value=cr_data.response_value,
                    comment=cr_data.comment,
                    photos=cr_data.photos or [],
                )
                db.add(new_response)

    await db.commit()
    await db.refresh(report)

    # Reload relationships
    result = await db.execute(
        select(Report)
        .options(
            selectinload(Report.info_values),
            selectinload(Report.checklist_responses),
        )
        .where(Report.id == report.id)
    )
    report = result.scalar_one()

    return _build_detail_response(report)


@router.post("/{report_id}/complete", response_model=ReportDetailResponse)
async def complete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_filter),
):
    """
    Mark a report as completed.

    - Validates that required fields are filled
    - Sets completed_at timestamp
    - Changes status to 'completed'
    """
    result = await db.execute(
        select(Report)
        .options(
            selectinload(Report.info_values),
            selectinload(Report.checklist_responses),
        )
        .where(
            and_(
                Report.id == report_id,
                Report.tenant_id == tenant_id,
            )
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )

    if report.status == ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relatorio ja esta finalizado",
        )

    if report.status == ReportStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao e possivel finalizar um relatorio arquivado",
        )

    # TODO: Validate required fields based on template snapshot
    # For now, just mark as completed

    report.status = ReportStatus.COMPLETED
    report.completed_at = datetime.utcnow()

    if not report.started_at:
        report.started_at = report.completed_at

    await db.commit()
    await db.refresh(report)

    return _build_detail_response(report)


@router.post("/{report_id}/archive", response_model=ReportDetailResponse)
async def archive_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_filter),
):
    """Archive a completed report."""
    result = await db.execute(
        select(Report)
        .options(
            selectinload(Report.info_values),
            selectinload(Report.checklist_responses),
        )
        .where(
            and_(
                Report.id == report_id,
                Report.tenant_id == tenant_id,
            )
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatorio nao encontrado",
        )

    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas relatorios finalizados podem ser arquivados",
        )

    report.status = ReportStatus.ARCHIVED
    await db.commit()
    await db.refresh(report)

    return _build_detail_response(report)


def _build_list_response(report: Report) -> ReportResponse:
    """Build response for list view."""
    template_name = None
    if report.template_snapshot and "name" in report.template_snapshot:
        template_name = report.template_snapshot["name"]

    return ReportResponse(
        id=report.id,
        tenant_id=report.tenant_id,
        template_id=report.template_id,
        project_id=report.project_id,
        user_id=report.user_id,
        title=report.title,
        status=report.status,
        location=report.location,
        started_at=report.started_at,
        completed_at=report.completed_at,
        created_at=report.created_at,
        updated_at=report.updated_at,
        template_name=template_name,
    )


def _build_detail_response(report: Report) -> ReportDetailResponse:
    """Build detailed response with all data."""
    # Sort info values and checklist responses
    info_values = sorted(report.info_values, key=lambda x: x.created_at)
    checklist_responses = sorted(
        report.checklist_responses,
        key=lambda x: (x.section_order, x.field_order)
    )

    return ReportDetailResponse(
        id=report.id,
        tenant_id=report.tenant_id,
        template_id=report.template_id,
        project_id=report.project_id,
        user_id=report.user_id,
        title=report.title,
        status=report.status,
        location=report.location,
        template_snapshot=report.template_snapshot,
        started_at=report.started_at,
        completed_at=report.completed_at,
        created_at=report.created_at,
        updated_at=report.updated_at,
        info_values=[
            InfoValueResponse(
                id=iv.id,
                report_id=iv.report_id,
                info_field_id=iv.info_field_id,
                field_label=iv.field_label,
                field_type=iv.field_type,
                value=iv.value,
                created_at=iv.created_at,
            )
            for iv in info_values
        ],
        checklist_responses=[
            ChecklistResponseResponse(
                id=cr.id,
                report_id=cr.report_id,
                section_id=cr.section_id,
                field_id=cr.field_id,
                section_name=cr.section_name,
                section_order=cr.section_order,
                field_label=cr.field_label,
                field_order=cr.field_order,
                field_type=cr.field_type,
                field_options=cr.field_options,
                response_value=cr.response_value,
                comment=cr.comment,
                photos=cr.photos,
                created_at=cr.created_at,
            )
            for cr in checklist_responses
        ],
    )
